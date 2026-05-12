from __future__ import annotations

from apps.bot.tts_listener_registry import TtsListenerRegistry


def test_registry_supports_multiple_users_per_guild() -> None:
    registry = TtsListenerRegistry()

    registry.add(guild_id=1, user_id=11)
    registry.add(guild_id=1, user_id=22)

    assert registry.contains(guild_id=1, user_id=11)
    assert registry.contains(guild_id=1, user_id=22)
    assert registry.list_users(guild_id=1) == {11, 22}


def test_remove_and_clear_are_scoped_to_guild() -> None:
    registry = TtsListenerRegistry()
    registry.add(guild_id=1, user_id=11)
    registry.add(guild_id=1, user_id=22)
    registry.add(guild_id=2, user_id=99)

    registry.remove(guild_id=1, user_id=11)
    registry.clear(guild_id=1)

    assert not registry.contains(guild_id=1, user_id=11)
    assert not registry.contains(guild_id=1, user_id=22)
    assert registry.contains(guild_id=2, user_id=99)
