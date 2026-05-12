"""In-memory guild session mappings for the Discord bot."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class GuildSessionState:
    """Mutable per-guild bot session state."""

    text_channel_id: int
    relay_enabled: bool = False


class SessionRegistry:
    """Track which text channel each guild's bot session is bound to."""

    def __init__(self) -> None:
        self._states: dict[int, GuildSessionState] = {}

    def upsert(self, guild_id: int, text_channel_id: int) -> None:
        existing = self._states.get(guild_id)
        if existing is None:
            self._states[guild_id] = GuildSessionState(text_channel_id=text_channel_id)
        else:
            existing.text_channel_id = text_channel_id

    def get(self, guild_id: int) -> int | None:
        state = self._states.get(guild_id)
        return state.text_channel_id if state is not None else None

    def get_state(self, guild_id: int) -> GuildSessionState | None:
        return self._states.get(guild_id)

    def remove(self, guild_id: int) -> int | None:
        state = self._states.pop(guild_id, None)
        return state.text_channel_id if state is not None else None

    def set_relay(self, guild_id: int, enabled: bool) -> bool:
        """Toggle the auto-relay flag. Returns True if the guild had a session."""
        state = self._states.get(guild_id)
        if state is None:
            return False
        state.relay_enabled = enabled
        return True

    def is_relay_enabled(self, guild_id: int) -> bool:
        state = self._states.get(guild_id)
        return bool(state and state.relay_enabled)
