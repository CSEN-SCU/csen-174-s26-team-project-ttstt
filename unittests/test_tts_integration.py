from __future__ import annotations

import pytest

from apps.bot.commands import BotCommandService
from apps.bot.preferences_store import InMemoryPreferencesStore, resolve_effective_voice_settings
from apps.bot.tts import TtsError, chunk_text_for_tts, validate_voice_settings


class FakeTtsClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def synthesize(self, text: str, voice_prefs: dict) -> bytes:
        self.calls.append((text, voice_prefs))
        return f"audio:{text}".encode("utf-8")


def test_validate_voice_settings_enforces_ranges() -> None:
    settings = validate_voice_settings({"voice": "TestVoice", "stability": 0.3, "speed": 1.1})
    assert settings["voice"] == "TestVoice"
    assert settings["stability"] == pytest.approx(0.3)
    assert settings["speed"] == pytest.approx(1.1)

    with pytest.raises(ValueError):
        validate_voice_settings({"voice": "", "stability": 0.3, "speed": 1.0})

    with pytest.raises(ValueError):
        validate_voice_settings({"voice": "TestVoice", "stability": 1.5, "speed": 1.0})

    with pytest.raises(ValueError):
        validate_voice_settings({"voice": "TestVoice", "stability": 0.5, "speed": 1.5})


def test_chunk_text_for_tts_preserves_order() -> None:
    chunks = chunk_text_for_tts("one two three four five six", max_chars=10)
    assert chunks
    assert all(len(chunk) <= 10 for chunk in chunks)
    assert " ".join(chunks).replace("  ", " ").strip() == "one two three four five six"


def test_resolve_effective_voice_settings_precedence() -> None:
    effective = resolve_effective_voice_settings(
        guild_default={"voice": "GuildVoice", "stability": 0.2, "speed": 0.9},
        user_override={"voice": "UserVoice"},
        system_default={"voice": "SystemVoice", "stability": 0.5, "speed": 1.0},
    )
    assert effective == {"voice": "UserVoice", "stability": 0.2, "speed": 0.9}


def test_command_service_applies_user_override_for_synthesis() -> None:
    fake_tts = FakeTtsClient()
    store = InMemoryPreferencesStore()
    service = BotCommandService(tts_client=fake_tts, preferences_store=store)

    service.set_guild_voice(7, "GuildVoice", stability=0.4, speed=1.0)
    service.set_user_voice(7, 42, "UserVoice", stability=0.8, speed=1.2)

    playback = service.synthesize_for_message(guild_id=7, user_id=42, text="hello world")
    assert playback
    assert fake_tts.calls[0][1] == {"voice": "UserVoice", "stability": 0.8, "speed": 1.2}


def test_command_service_raises_safe_error_if_provider_fails() -> None:
    class BrokenClient:
        def synthesize(self, text: str, voice_prefs: dict) -> bytes:
            raise RuntimeError("provider timeout")

    service = BotCommandService(tts_client=BrokenClient(), preferences_store=InMemoryPreferencesStore())
    with pytest.raises(TtsError):
        service.synthesize_for_message(guild_id=1, user_id=2, text="hello")
