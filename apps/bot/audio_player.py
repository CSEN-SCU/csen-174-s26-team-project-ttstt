"""Per-guild audio playback queue for synthesized speech."""

from __future__ import annotations

import asyncio
import io
import logging
from typing import Protocol

import discord

LOGGER = logging.getLogger("ttstt-bot.audio")


class _BotLike(Protocol):
    """Subset of ``commands.Bot`` the player needs (kept small for testing)."""

    def get_guild(self, guild_id: int) -> discord.Guild | None: ...


class GuildAudioPlayer:
    """Serialize MP3 playback per guild over an existing voice client.

    Each guild gets its own ``asyncio.Queue`` and worker task so playback
    requests in one server never block another. Workers exit after a brief
    idle window and are re-spawned on the next ``enqueue`` to avoid leaking
    tasks for inactive guilds.
    """

    IDLE_TIMEOUT_S = 60.0

    def __init__(self, bot: _BotLike, ffmpeg_executable: str = "ffmpeg") -> None:
        self._bot = bot
        self._ffmpeg_executable = ffmpeg_executable
        self._queues: dict[int, asyncio.Queue[bytes]] = {}
        self._workers: dict[int, asyncio.Task[None]] = {}

    async def enqueue(self, guild_id: int, audio_bytes: bytes) -> None:
        if not audio_bytes:
            return
        queue = self._queues.setdefault(guild_id, asyncio.Queue())
        await queue.put(audio_bytes)
        worker = self._workers.get(guild_id)
        if worker is None or worker.done():
            self._workers[guild_id] = asyncio.create_task(
                self._worker(guild_id), name=f"audio-player-{guild_id}"
            )

    async def drain(self, guild_id: int) -> None:
        """Wait for any queued audio for ``guild_id`` to finish playing."""
        queue = self._queues.get(guild_id)
        if queue is None:
            return
        await queue.join()

    async def shutdown(self) -> None:
        for worker in list(self._workers.values()):
            worker.cancel()
        for worker in list(self._workers.values()):
            try:
                await worker
            except (asyncio.CancelledError, Exception):
                pass
        self._workers.clear()
        self._queues.clear()

    async def _worker(self, guild_id: int) -> None:
        queue = self._queues[guild_id]
        loop = asyncio.get_running_loop()

        while True:
            try:
                audio = await asyncio.wait_for(queue.get(), timeout=self.IDLE_TIMEOUT_S)
            except asyncio.TimeoutError:
                return

            try:
                guild = self._bot.get_guild(guild_id)
                voice_client = guild.voice_client if guild else None
                if voice_client is None or not voice_client.is_connected():
                    LOGGER.info("Dropping audio for guild=%s: not connected", guild_id)
                    continue

                while voice_client.is_playing():
                    await asyncio.sleep(0.1)

                source = discord.FFmpegPCMAudio(
                    source=io.BytesIO(audio),
                    pipe=True,
                    executable=self._ffmpeg_executable,
                    options="-loglevel error",
                )
                done = asyncio.Event()

                def _after_play(err: BaseException | None) -> None:
                    if err is not None:
                        LOGGER.warning("Playback error guild=%s: %r", guild_id, err)
                    loop.call_soon_threadsafe(done.set)

                voice_client.play(source, after=_after_play)
                await done.wait()
            except Exception:
                LOGGER.exception("Unexpected playback failure guild=%s", guild_id)
            finally:
                queue.task_done()
