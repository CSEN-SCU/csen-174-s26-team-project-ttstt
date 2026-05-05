"""Web-facing settings handlers shared with command service."""

from __future__ import annotations

from typing import Any

from apps.bot.commands import BotCommandService
from apps.bot.tts import list_voices


def get_voice_catalog() -> dict[str, list[dict[str, Any]]]:
    """Return available voices for web/Discord configuration UIs."""
    return {"voices": list_voices()}


def update_guild_voice_settings(
    service: BotCommandService,
    *,
    guild_id: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Apply guild defaults from a web settings payload."""
    return service.set_guild_voice(
        guild_id,
        str(payload["voice"]),
        stability=float(payload["stability"]),
        speed=float(payload["speed"]),
    )


def update_user_voice_settings(
    service: BotCommandService,
    *,
    guild_id: int,
    user_id: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Apply per-user runtime overrides from a web settings payload."""
    return service.set_user_voice(
        guild_id,
        user_id,
        str(payload["voice"]),
        stability=float(payload["stability"]),
        speed=float(payload["speed"]),
    )
