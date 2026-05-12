from __future__ import annotations

from apps.bot.playback import GuildPlaybackQueue


def test_guild_queue_is_fifo_with_monotonic_sequence() -> None:
    queue = GuildPlaybackQueue()

    first = queue.enqueue(guild_id=7, audio_bytes=b"a", source_user_id=101, source_message_id=1001)
    second = queue.enqueue(guild_id=7, audio_bytes=b"b", source_user_id=202, source_message_id=1002)

    popped_1 = queue.pop_next(guild_id=7)
    popped_2 = queue.pop_next(guild_id=7)

    assert first.sequence_id == 1
    assert second.sequence_id == 2
    assert popped_1 == first
    assert popped_2 == second


def test_guild_queues_are_isolated() -> None:
    queue = GuildPlaybackQueue()

    one = queue.enqueue(guild_id=1, audio_bytes=b"a", source_user_id=101, source_message_id=1001)
    two = queue.enqueue(guild_id=2, audio_bytes=b"b", source_user_id=202, source_message_id=1002)

    assert queue.pop_next(guild_id=1) == one
    assert queue.pop_next(guild_id=2) == two
