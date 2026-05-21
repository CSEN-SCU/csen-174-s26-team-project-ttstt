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

# Featured Aura 2 English voices (Deepgram docs); autocomplete also accepts any model id.
FEATURED_AURA2_VOICES: tuple[str, ...] = (
    "aura-2-thalia-en",
    "aura-2-andromeda-en",
    "aura-2-helena-en",
    "aura-2-apollo-en",
    "aura-2-arcas-en",
    "aura-2-aries-en",
    "aura-2-asteria-en",
    "aura-2-athena-en",
    "aura-2-atlas-en",
    "aura-2-aurora-en",
    "aura-2-callista-en",
    "aura-2-cora-en",
)

STYLE_CLEAR_TOKENS = frozenset({"", "none", "default", "clear"})

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


def merge_voice_preferences(
    existing: VoicePreferences,
    *,
    voice: str | None = None,
    speed: float | None = None,
    pitch: float | None = None,
    style: str | None = None,
) -> VoicePreferences:
    """Apply partial updates; style tokens none/default/clear remove the style."""

    new_voice = existing.voice
    if voice is not None:
        new_voice = voice.strip()

    new_speed = existing.speed if speed is None else speed
    new_pitch = existing.pitch if pitch is None else pitch

    new_style = existing.style
    if style is not None:
        stripped = style.strip()
        if stripped.lower() in STYLE_CLEAR_TOKENS:
            new_style = None
        else:
            new_style = stripped

    return VoicePreferences(voice=new_voice, speed=new_speed, pitch=new_pitch, style=new_style)


def format_voice_settings_message(prefs: VoicePreferences, *, prefix: str) -> str:
    return (
        f"{prefix}: voice=`{prefs.voice}`, speed={prefs.speed}, pitch={prefs.pitch}, "
        f"style={prefs.style or 'default'}."
    )


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
