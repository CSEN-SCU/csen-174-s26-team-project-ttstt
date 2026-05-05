"""Command-level orchestration for TTS settings and playback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps.bot.preferences_store import InMemoryPreferencesStore, resolve_effective_voice_settings
from apps.bot.tts import TtsClient, chunk_text_for_tts, synthesize_text, validate_voice_settings


DEFAULT_VOICE_SETTINGS = {"voice": "Rachel", "stability": 0.5, "speed": 1.0}


@dataclass(frozen=True)
class PlaybackChunk:
    """Single audio chunk ready for Discord playback."""

    text: str
    audio: bytes


class BotCommandService:
    """Shared command handlers for Discord and web entrypoints."""

    def __init__(
        self,
        *,
        tts_client: TtsClient,
        preferences_store: InMemoryPreferencesStore,
        default_voice_settings: dict[str, Any] | None = None,
    ) -> None:
        self._tts_client = tts_client
        self._preferences = preferences_store
        self._system_default = default_voice_settings or dict(DEFAULT_VOICE_SETTINGS)

    def set_guild_voice(self, guild_id: int, voice: str, *, stability: float, speed: float) -> dict[str, Any]:
        settings = validate_voice_settings({"voice": voice, "stability": stability, "speed": speed})
        self._preferences.set_guild_defaults(guild_id, settings)
        return settings

    def set_user_voice(self, guild_id: int, user_id: int, voice: str, *, stability: float, speed: float) -> dict[str, Any]:
        settings = validate_voice_settings({"voice": voice, "stability": stability, "speed": speed})
        self._preferences.set_user_override(guild_id, user_id, settings)
        return settings

    def get_effective_voice_settings(self, guild_id: int, user_id: int) -> dict[str, Any]:
        return resolve_effective_voice_settings(
            guild_default=self._preferences.get_guild_defaults(guild_id),
            user_override=self._preferences.get_user_override(guild_id, user_id),
            system_default=self._system_default,
        )

    def synthesize_for_message(
        self, *, guild_id: int, user_id: int, text: str, max_chars: int = 280
    ) -> list[PlaybackChunk]:
        prefs = self.get_effective_voice_settings(guild_id, user_id)
        chunks = chunk_text_for_tts(text, max_chars=max_chars)
        return [
            PlaybackChunk(text=chunk, audio=synthesize_text(chunk, prefs, self._tts_client))
            for chunk in chunks
        ]
