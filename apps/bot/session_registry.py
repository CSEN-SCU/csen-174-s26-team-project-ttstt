"""In-memory guild session mappings for the Discord bot."""

from __future__ import annotations


class SessionRegistry:
    """Track which text channel each guild's bot session is bound to."""

    def __init__(self) -> None:
        self._text_channels_by_guild: dict[int, int] = {}

    def upsert(self, guild_id: int, text_channel_id: int) -> None:
        self._text_channels_by_guild[guild_id] = text_channel_id

    def get(self, guild_id: int) -> int | None:
        return self._text_channels_by_guild.get(guild_id)

    def remove(self, guild_id: int) -> int | None:
        return self._text_channels_by_guild.pop(guild_id, None)
