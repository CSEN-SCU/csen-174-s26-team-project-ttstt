from __future__ import annotations

from apps.bot.playback import GuildPlaybackQueue, PlaybackCoordinator


class _FakeBot:
    def is_closed(self) -> bool:
        return False


def test_playback_item_records_enqueue_timestamp() -> None:
    queue = GuildPlaybackQueue()

    item = queue.enqueue(guild_id=5, audio_bytes=b"a", source_user_id=10, source_message_id=99)

    assert item.enqueued_at_monotonic > 0.0


def test_playback_coordinator_latency_metric_defaults_to_none() -> None:
    coordinator = PlaybackCoordinator(bot=_FakeBot())

    assert coordinator.get_last_enqueue_to_playback_delay(5) is None
