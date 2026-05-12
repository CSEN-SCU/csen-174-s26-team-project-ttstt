"""Track per-guild users whose text should be read aloud."""

from __future__ import annotations


class TtsListenerRegistry:
    """In-memory registry of listened users per guild."""

    def __init__(self) -> None:
        self._users_by_guild: dict[int, set[int]] = {}

    def add(self, guild_id: int, user_id: int) -> None:
        self._users_by_guild.setdefault(guild_id, set()).add(user_id)

    def remove(self, guild_id: int, user_id: int) -> bool:
        users = self._users_by_guild.get(guild_id)
        if not users or user_id not in users:
            return False
        users.remove(user_id)
        if not users:
            self._users_by_guild.pop(guild_id, None)
        return True

    def clear(self, guild_id: int) -> set[int]:
        return set(self._users_by_guild.pop(guild_id, set()))

    def contains(self, guild_id: int, user_id: int) -> bool:
        return user_id in self._users_by_guild.get(guild_id, set())

    def list_users(self, guild_id: int) -> set[int]:
        return set(self._users_by_guild.get(guild_id, set()))
