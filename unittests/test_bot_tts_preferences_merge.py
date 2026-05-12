from __future__ import annotations

from apps.bot.main import _merge_preferences
from apps.bot.voice_preferences import VoicePreferences


def test_merge_preferences_overrides_only_provided_fields() -> None:
    current = VoicePreferences(voice="aura-2-thalia-en", speed=1.0, pitch=0.0, style="warm")

    merged = _merge_preferences(
        existing=current,
        voice=None,
        speed=1.4,
        pitch=None,
        style="calm",
    )

    assert merged.voice == "aura-2-thalia-en"
    assert merged.speed == 1.4
    assert merged.pitch == 0.0
    assert merged.style == "calm"
