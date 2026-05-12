"""Audio queue and sequential playback worker for Discord voice clients."""

from __future__ import annotations

import asyncio
import io
import logging
from collections import defaultdict, deque
from dataclasses import dataclass

import discord

LOGGER = logging.getLogger("ttstt-bot.playback")


@dataclass(frozen=True, slots=True)
class PlaybackItem:
    guild_id: int
    sequence_id: int
    audio_bytes: bytes
    source_user_id: int
    source_message_id: int


class GuildPlaybackQueue:
    """Per-guild FIFO queue that assigns monotonic sequence IDs."""

    def __init__(self) -> None:
        self._items_by_guild: dict[int, deque[PlaybackItem]] = defaultdict(deque)
        self._sequence_by_guild: dict[int, int] = defaultdict(int)

    def enqueue(self, guild_id: int, audio_bytes: bytes, source_user_id: int, source_message_id: int) -> PlaybackItem:
        sequence_id = self._sequence_by_guild[guild_id] + 1
        self._sequence_by_guild[guild_id] = sequence_id
        item = PlaybackItem(
            guild_id=guild_id,
            sequence_id=sequence_id,
            audio_bytes=audio_bytes,
            source_user_id=source_user_id,
            source_message_id=source_message_id,
        )
        self._items_by_guild[guild_id].append(item)
        return item

    def pop_next(self, guild_id: int) -> PlaybackItem | None:
        queue = self._items_by_guild.get(guild_id)
        if not queue:
            return None
        item = queue.popleft()
        if not queue:
            self._items_by_guild.pop(guild_id, None)
        return item

    def has_items(self, guild_id: int) -> bool:
        return bool(self._items_by_guild.get(guild_id))

    def clear_guild(self, guild_id: int) -> list[PlaybackItem]:
        queue = self._items_by_guild.pop(guild_id, deque())
        return list(queue)


class PlaybackCoordinator:
    """Consumes per-guild queue items and plays them sequentially in voice."""

    def __init__(self, bot: discord.Client, ffmpeg_executable: str = "ffmpeg") -> None:
        self._bot = bot
        self._ffmpeg_executable = ffmpeg_executable
        self._queue = GuildPlaybackQueue()
        self._wake_events: dict[int, asyncio.Event] = {}
        self._worker_tasks: dict[int, asyncio.Task[None]] = {}
        self._last_played_sequence: dict[int, int] = defaultdict(int)

    def enqueue(self, guild_id: int, audio_bytes: bytes, source_user_id: int, source_message_id: int) -> PlaybackItem:
        item = self._queue.enqueue(
            guild_id=guild_id,
            audio_bytes=audio_bytes,
            source_user_id=source_user_id,
            source_message_id=source_message_id,
        )
        self._wake_events.setdefault(guild_id, asyncio.Event()).set()
        self._ensure_worker(guild_id)
        return item

    def clear_guild(self, guild_id: int) -> list[PlaybackItem]:
        return self._queue.clear_guild(guild_id)

    async def shutdown(self) -> None:
        for event in self._wake_events.values():
            event.set()
        tasks = list(self._worker_tasks.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._worker_tasks.clear()
        self._wake_events.clear()

    def _ensure_worker(self, guild_id: int) -> None:
        task = self._worker_tasks.get(guild_id)
        if task is None or task.done():
            self._worker_tasks[guild_id] = asyncio.create_task(self._worker_loop(guild_id))

    async def _worker_loop(self, guild_id: int) -> None:
        wake_event = self._wake_events.setdefault(guild_id, asyncio.Event())
        while not self._bot.is_closed():
            item = self._queue.pop_next(guild_id)
            if item is None:
                wake_event.clear()
                await wake_event.wait()
                continue
            await self._play_item(item)

    async def _play_item(self, item: PlaybackItem) -> None:
        expected = self._last_played_sequence[item.guild_id] + 1
        if item.sequence_id != expected:
            LOGGER.warning(
                "Out-of-order playback item guild=%s expected=%s got=%s",
                item.guild_id,
                expected,
                item.sequence_id,
            )

        guild = self._bot.get_guild(item.guild_id)
        voice_client = guild.voice_client if guild is not None else None
        if voice_client is None or not voice_client.is_connected():
            LOGGER.warning("Dropping queued audio for guild=%s because voice is disconnected", item.guild_id)
            return

        source = discord.FFmpegPCMAudio(
            source=io.BytesIO(item.audio_bytes),
            pipe=True,
            executable=self._ffmpeg_executable,
            options="-loglevel error",
        )
        done = asyncio.Event()

        def after_play(error: Exception | None) -> None:
            if error is not None:
                LOGGER.warning("Playback failed for guild=%s sequence=%s error=%r", item.guild_id, item.sequence_id, error)
            self._bot.loop.call_soon_threadsafe(done.set)

        voice_client.play(source, after=after_play)
        await done.wait()
        self._last_played_sequence[item.guild_id] = item.sequence_id
