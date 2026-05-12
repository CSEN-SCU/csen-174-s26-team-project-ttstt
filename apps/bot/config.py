"""Environment-backed configuration for the Discord bot runtime."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BotConfig:
    discord_token: str
    discord_guild_id: int | None
    elevenlabs_api_key: str
    elevenlabs_voice_id: str
    elevenlabs_model_id: str = "eleven_turbo_v2_5"
    elevenlabs_stability: float | None = None
    elevenlabs_similarity_boost: float | None = None
    tts_max_chars_per_message: int = 500
    tts_max_chars_per_chunk: int = 240
    ffmpeg_executable: str = "ffmpeg"


def _parse_optional_int(value: str | None, field_name: str) -> int | None:
    if value is None or not value.strip():
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an integer when provided.") from exc


def _parse_optional_float(value: str | None, field_name: str) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a number when provided.") from exc


def _parse_positive_int(value: str | None, field_name: str, default: int) -> int:
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an integer when provided.") from exc
    if parsed <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")
    return parsed


def _require(env_name: str, *aliases: str) -> str:
    for name in (env_name, *aliases):
        value = os.getenv(name)
        if value is not None and value.strip():
            return value.strip()
    raise ValueError(f"{env_name} is required.")


def load_bot_config() -> BotConfig:
    """Load bot config from environment variables."""
    discord_token = _require("DISCORD_TOKEN", "DISCORD_BOT_TOKEN")
    elevenlabs_api_key = _require("ELEVENLABS_API_KEY")
    elevenlabs_voice_id = _require("ELEVENLABS_VOICE_ID")

    discord_guild_id = _parse_optional_int(os.getenv("DISCORD_GUILD_ID"), "DISCORD_GUILD_ID")
    elevenlabs_model_id = (os.getenv("ELEVENLABS_MODEL_ID") or "eleven_turbo_v2_5").strip()
    elevenlabs_stability = _parse_optional_float(
        os.getenv("ELEVENLABS_STABILITY"), "ELEVENLABS_STABILITY"
    )
    elevenlabs_similarity_boost = _parse_optional_float(
        os.getenv("ELEVENLABS_SIMILARITY_BOOST"), "ELEVENLABS_SIMILARITY_BOOST"
    )
    tts_max_chars_per_message = _parse_positive_int(
        os.getenv("TTS_MAX_CHARS_PER_MESSAGE"), "TTS_MAX_CHARS_PER_MESSAGE", 500
    )
    tts_max_chars_per_chunk = _parse_positive_int(
        os.getenv("TTS_MAX_CHARS_PER_CHUNK"), "TTS_MAX_CHARS_PER_CHUNK", 240
    )
    ffmpeg_executable = (os.getenv("FFMPEG_EXECUTABLE") or "ffmpeg").strip()

    return BotConfig(
        discord_token=discord_token,
        discord_guild_id=discord_guild_id,
        elevenlabs_api_key=elevenlabs_api_key,
        elevenlabs_voice_id=elevenlabs_voice_id,
        elevenlabs_model_id=elevenlabs_model_id,
        elevenlabs_stability=elevenlabs_stability,
        elevenlabs_similarity_boost=elevenlabs_similarity_boost,
        tts_max_chars_per_message=tts_max_chars_per_message,
        tts_max_chars_per_chunk=tts_max_chars_per_chunk,
        ffmpeg_executable=ffmpeg_executable,
    )
