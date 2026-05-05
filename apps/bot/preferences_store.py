"""Guild/user voice preference storage helpers."""

from __future__ import annotations

from typing import Any, Protocol


class PreferencesStore(Protocol):
    """Persistence contract for bot preference resolution."""

    def get_guild_defaults(self, guild_id: int) -> dict[str, Any] | None:
        """Fetch guild-level voice defaults."""

    def set_guild_defaults(self, guild_id: int, settings: dict[str, Any]) -> None:
        """Persist guild-level voice defaults."""


class InMemoryPreferencesStore:
    """Temporary user + guild preference store for local runtime."""

    def __init__(self) -> None:
        self._guild_defaults: dict[int, dict[str, Any]] = {}
        self._user_overrides: dict[tuple[int, int], dict[str, Any]] = {}

    def get_guild_defaults(self, guild_id: int) -> dict[str, Any] | None:
        stored = self._guild_defaults.get(guild_id)
        return None if stored is None else dict(stored)

    def set_guild_defaults(self, guild_id: int, settings: dict[str, Any]) -> None:
        self._guild_defaults[guild_id] = dict(settings)

    def get_user_override(self, guild_id: int, user_id: int) -> dict[str, Any] | None:
        stored = self._user_overrides.get((guild_id, user_id))
        return None if stored is None else dict(stored)

    def set_user_override(self, guild_id: int, user_id: int, settings: dict[str, Any]) -> None:
        self._user_overrides[(guild_id, user_id)] = dict(settings)


class PostgresPreferencesStore:
    """
    Postgres-backed guild defaults.

    Uses a DB-API 2.0 style connection object (e.g., psycopg connection).
    """

    def __init__(self, connection: Any) -> None:
        self._connection = connection

    def get_guild_defaults(self, guild_id: int) -> dict[str, Any] | None:
        with self._connection.cursor() as cur:
            cur.execute(
                """
                SELECT voice_id, stability, speed
                FROM guild_voice_defaults
                WHERE guild_id = %s
                """,
                (guild_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        voice_id, stability, speed = row
        return {"voice": voice_id, "stability": float(stability), "speed": float(speed)}

    def set_guild_defaults(self, guild_id: int, settings: dict[str, Any]) -> None:
        with self._connection.cursor() as cur:
            cur.execute(
                """
                INSERT INTO guild_voice_defaults (guild_id, voice_id, stability, speed, updated_at)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (guild_id)
                DO UPDATE SET
                    voice_id = EXCLUDED.voice_id,
                    stability = EXCLUDED.stability,
                    speed = EXCLUDED.speed,
                    updated_at = NOW()
                """,
                (guild_id, settings["voice"], settings["stability"], settings["speed"]),
            )
        self._connection.commit()


def resolve_effective_voice_settings(
    *,
    guild_default: dict[str, Any] | None,
    user_override: dict[str, Any] | None,
    system_default: dict[str, Any],
) -> dict[str, Any]:
    """Apply precedence: user override -> guild default -> system default."""
    effective = dict(system_default)
    if guild_default:
        effective.update(guild_default)
    if user_override:
        effective.update(user_override)
    return effective
