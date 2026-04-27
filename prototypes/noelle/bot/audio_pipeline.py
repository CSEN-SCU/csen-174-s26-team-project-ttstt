"""Audio receive sink and buffering utilities."""

from __future__ import annotations

import asyncio
import io
import threading
import time
import wave
from dataclasses import dataclass, field
from typing import Awaitable, Callable

import discord
from discord.ext import voice_recv


SegmentHandler = Callable[[discord.Member, bytes], Awaitable[None]]


@dataclass(slots=True)
class _UserBuffer:
    member: discord.Member
    pcm_data: bytearray = field(default_factory=bytearray)
    last_packet_at: float = 0.0


class BufferedTranscriptionSink(voice_recv.AudioSink):
    """Collect PCM packets per user and flush after short silence gaps."""

    def __init__(
        self,
        segment_handler: SegmentHandler,
        *,
        silence_timeout_s: float = 1.1,
        flush_interval_s: float = 0.35,
        min_chunk_bytes: int = 12_000,
    ) -> None:
        super().__init__()
        self._segment_handler = segment_handler
        self._silence_timeout_s = silence_timeout_s
        self._flush_interval_s = flush_interval_s
        self._min_chunk_bytes = min_chunk_bytes

        self._buffers: dict[int, _UserBuffer] = {}
        self._lock = threading.Lock()
        self._runner_task: asyncio.Task[None] | None = None
        self._running = False

    def wants_opus(self) -> bool:
        return False

    def write(self, user: discord.Member | discord.User | None, data: voice_recv.VoiceData) -> None:
        """Called from the voice receive thread for each audio packet."""

        if user is None or data.pcm is None or not isinstance(user, discord.Member):
            return

        now = time.monotonic()
        with self._lock:
            state = self._buffers.get(user.id)
            if state is None:
                state = _UserBuffer(member=user)
                self._buffers[user.id] = state

            state.member = user
            state.pcm_data.extend(data.pcm)
            state.last_packet_at = now

    def cleanup(self) -> None:
        self._running = False

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._runner_task = asyncio.create_task(self._flush_loop())

    async def stop(self) -> None:
        self._running = False
        if self._runner_task is not None:
            self._runner_task.cancel()
            try:
                await self._runner_task
            except asyncio.CancelledError:
                pass
            self._runner_task = None

    async def _flush_loop(self) -> None:
        while self._running:
            await asyncio.sleep(self._flush_interval_s)
            for member, pcm in self._collect_ready_segments():
                await self._segment_handler(member, pcm)

    def _collect_ready_segments(self) -> list[tuple[discord.Member, bytes]]:
        now = time.monotonic()
        ready: list[tuple[discord.Member, bytes]] = []

        with self._lock:
            removable_ids: list[int] = []
            for user_id, state in self._buffers.items():
                silent_for = now - state.last_packet_at
                if silent_for < self._silence_timeout_s:
                    continue

                pcm_bytes = bytes(state.pcm_data)
                removable_ids.append(user_id)

                if len(pcm_bytes) >= self._min_chunk_bytes:
                    ready.append((state.member, pcm_bytes))

            for user_id in removable_ids:
                self._buffers.pop(user_id, None)

        return ready


def pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 48_000, channels: int = 2, sample_width: int = 2) -> bytes:
    """Wrap raw PCM bytes in a WAV container for Deepgram."""

    with io.BytesIO() as buffer:
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_bytes)
        return buffer.getvalue()
