"""User voice preferences and persistence for TTS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

DEFAULT_VOICE = "aura-2-thalia-en"
DEFAULT_SPEED = 1.0
DEFAULT_PITCH = 0.0
DEFAULT_STYLE: str | None = None

MIN_SPEED = 0.5
MAX_SPEED = 2.0
MIN_PITCH = -20.0
MAX_PITCH = 20.0

UPSERT_PREFERENCES_SQL = """
INSERT INTO bot_voice_preferences (
    guild_id,
    user_id,
    voice,
    speed,
    pitch,
    style
) VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (guild_id, user_id)
DO UPDATE SET
    voice = EXCLUDED.voice,
    speed = EXCLUDED.speed,
    pitch = EXCLUDED.pitch,
    style = EXCLUDED.style,
    updated_at = NOW();
"""

SELECT_PREFERENCES_SQL = """
SELECT voice, speed, pitch, style
FROM bot_voice_preferences
WHERE guild_id = $1 AND user_id = $2;
"""


@dataclass(frozen=True, slots=True)
class VoicePreferences:
    voice: str
    speed: float
    pitch: float
    style: str | None = None

    @classmethod
    def defaults(cls) -> "VoicePreferences":
        return cls(
            voice=DEFAULT_VOICE,
            speed=DEFAULT_SPEED,
            pitch=DEFAULT_PITCH,
            style=DEFAULT_STYLE,
        )

    def validate(self) -> None:
        if not self.voice.strip():
            raise ValueError("voice must be non-empty")
        if not (MIN_SPEED <= self.speed <= MAX_SPEED):
            raise ValueError(f"speed must be between {MIN_SPEED} and {MAX_SPEED}")
        if not (MIN_PITCH <= self.pitch <= MAX_PITCH):
            raise ValueError(f"pitch must be between {MIN_PITCH} and {MAX_PITCH}")
        if self.style is not None and not self.style.strip():
            raise ValueError("style must be non-empty when provided")

    def to_provider_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "voice": self.voice,
            "speed": self.speed,
            "pitch": self.pitch,
        }
        if self.style:
            payload["style"] = self.style
        return payload


class VoicePreferencesRepository(Protocol):
    async def get(self, guild_id: int, user_id: int) -> VoicePreferences:
        ...

    async def upsert(self, guild_id: int, user_id: int, prefs: VoicePreferences) -> VoicePreferences:
        ...

    async def reset(self, guild_id: int, user_id: int) -> VoicePreferences:
        ...


class PostgresVoicePreferencesRepository:
    """Postgres-backed preference repository using a conn/pool object."""

    def __init__(self, conn: object) -> None:
        self._conn = conn

    async def get(self, guild_id: int, user_id: int) -> VoicePreferences:
        row = await self._conn.fetchrow(SELECT_PREFERENCES_SQL, guild_id, user_id)
        if row is None:
            return VoicePreferences.defaults()
        return VoicePreferences(
            voice=str(row["voice"]),
            speed=float(row["speed"]),
            pitch=float(row["pitch"]),
            style=str(row["style"]) if row["style"] is not None else None,
        )

    async def upsert(self, guild_id: int, user_id: int, prefs: VoicePreferences) -> VoicePreferences:
        prefs.validate()
        await self._conn.execute(
            UPSERT_PREFERENCES_SQL,
            guild_id,
            user_id,
            prefs.voice,
            prefs.speed,
            prefs.pitch,
            prefs.style,
        )
        return prefs

    async def reset(self, guild_id: int, user_id: int) -> VoicePreferences:
        defaults = VoicePreferences.defaults()
        return await self.upsert(guild_id=guild_id, user_id=user_id, prefs=defaults)
