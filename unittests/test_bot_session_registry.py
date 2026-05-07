from __future__ import annotations

from apps.bot.session_registry import SessionRegistry


def test_upsert_and_get_session() -> None:
    registry = SessionRegistry()

    registry.upsert(guild_id=123, text_channel_id=456)

    assert registry.get(123) == 456


def test_remove_session_returns_previous_channel() -> None:
    registry = SessionRegistry()
    registry.upsert(guild_id=99, text_channel_id=1001)

    removed = registry.remove(99)

    assert removed == 1001
    assert registry.get(99) is None
