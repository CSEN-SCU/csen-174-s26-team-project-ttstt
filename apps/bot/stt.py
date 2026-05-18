"""Voice-receive audio sink that buffers user speech and posts STT transcriptions."""

from __future__ import annotations

import asyncio
import io
import logging
import wave
from collections import defaultdict
from typing import TYPE_CHECKING

import discord
from discord.ext import voice_recv

from apps.bot.content_moderation import (
    Disposition,
    format_sensitive_dm,
    moderate_for_transcript,
)
from apps.bot.transcription import AsrTranscriptionError, transcribe_audio

if TYPE_CHECKING:
    from apps.bot.transcription import AsrClient

LOGGER = logging.getLogger("ttstt-bot.stt")

_SAMPLE_RATE = 48_000
_CHANNELS = 2
_SAMPLE_WIDTH = 2  # 16-bit signed LE
SILENCE_TIMEOUT = 0.8  # seconds of silence before flushing an utterance
MIN_PCM_BYTES = int(_SAMPLE_RATE * _CHANNELS * _SAMPLE_WIDTH * 0.25)  # 250 ms minimum


def _wrap_pcm_as_wav(pcm: bytes) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(_CHANNELS)
        wf.setsampwidth(_SAMPLE_WIDTH)
        wf.setframerate(_SAMPLE_RATE)
        wf.writeframes(pcm)
    buf.seek(0)
    return buf.read()


class _UserBuffer:
    __slots__ = ("pcm", "seq")

    def __init__(self) -> None:
        self.pcm: bytearray = bytearray()
        self.seq: int = 0

    def add(self, chunk: bytes) -> int:
        self.pcm.extend(chunk)
        self.seq += 1
        return self.seq

    def collect(self) -> bytes:
        data = bytes(self.pcm)
        self.pcm.clear()
        return data


class SttListenerRegistry:
    """Track which users' voices should be transcribed per guild."""

    def __init__(self) -> None:
        self._users: dict[int, set[int]] = defaultdict(set)

    def add(self, guild_id: int, user_id: int) -> None:
        self._users[guild_id].add(user_id)

    def remove(self, guild_id: int, user_id: int) -> bool:
        s = self._users.get(guild_id)
        if not s or user_id not in s:
            return False
        s.discard(user_id)
        return True

    def contains(self, guild_id: int, user_id: int) -> bool:
        return user_id in self._users.get(guild_id, set())

    def clear(self, guild_id: int) -> set[int]:
        return self._users.pop(guild_id, set())

    def list_users(self, guild_id: int) -> set[int]:
        return set(self._users.get(guild_id, set()))


class TranscriptionSink(voice_recv.AudioSink):
    """
    Buffers per-user PCM audio, detects utterance end via a silence timeout,
    transcribes with the injected ASR client, and posts to the control channel.

    write() is called from the voice-receive thread; all async work is
    scheduled onto the bot's event loop via run_coroutine_threadsafe.
    """

    def __init__(
        self,
        *,
        asr_client: AsrClient,
        listeners: SttListenerRegistry,
        guild_id: int,
        text_channel_id: int,
        openai_api_key: str | None = None,
    ) -> None:
        super().__init__()
        self._asr_client = asr_client
        self._listeners = listeners
        self._guild_id = guild_id
        self._text_channel_id = text_channel_id
        self._openai_api_key = openai_api_key
        self._buffers: dict[int, _UserBuffer] = {}

    def wants_opus(self) -> bool:
        return False

    def write(self, user: discord.User | None, data: voice_recv.VoiceData) -> None:
        if user is None or not self._listeners.contains(self._guild_id, user.id):
            return

        buf = self._buffers.setdefault(user.id, _UserBuffer())
        seq = buf.add(data.pcm)

        assert self.client is not None
        asyncio.run_coroutine_threadsafe(
            self._flush_after_silence(user, buf, seq),
            self.client.loop,
        )

    async def _flush_after_silence(
        self, user: discord.User, buf: _UserBuffer, seq: int
    ) -> None:
        await asyncio.sleep(SILENCE_TIMEOUT)
        if buf.seq != seq:
            return  # newer audio arrived since this timer was scheduled

        pcm = buf.collect()
        if len(pcm) < MIN_PCM_BYTES:
            return

        wav = _wrap_pcm_as_wav(pcm)
        try:
            text = await asyncio.to_thread(transcribe_audio, wav, self._asr_client)
        except AsrTranscriptionError as exc:
            LOGGER.warning("STT failed for user=%s: %s", user.id, exc)
            return
        except Exception as exc:
            LOGGER.warning("Unexpected STT error for user=%s: %s", user.id, exc)
            return

        if not text:
            return

        outcome = moderate_for_transcript(text, openai_api_key=self._openai_api_key)
        if outcome.disposition is Disposition.BLOCKED:
            LOGGER.info("Suppressed transcript for user=%s (%s)", user.id, outcome.log_reason)
            return

        if outcome.disposition is Disposition.PRIVATE_DM:
            dm_body = outcome.dm_body or text
            try:
                await user.send(
                    format_sensitive_dm(dm_body, outcome.crisis_footer),
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            except discord.Forbidden:
                LOGGER.warning("Sensitive transcript for user=%s could not be delivered via DM", user.id)
            return

        channel = self.client.get_channel(self._text_channel_id)  # type: ignore[union-attr]
        if not isinstance(channel, discord.TextChannel):
            return

        public_text = outcome.public_text or text
        await channel.send(
            f"**{user.display_name}**: {public_text}",
            allowed_mentions=discord.AllowedMentions.none(),
        )

    def cleanup(self) -> None:
        self._buffers.clear()
