from __future__ import annotations

from apps.bot.voice_preferences import VoicePreferences, merge_voice_preferences


def test_merge_preferences_overrides_only_provided_fields() -> None:
    current = VoicePreferences(voice="aura-2-thalia-en", speed=1.0, pitch=0.0, style="warm")

    merged = merge_voice_preferences(
        current,
        voice=None,
        speed=1.4,
        pitch=None,
        style="calm",
    )

    assert merged.voice == "aura-2-thalia-en"
    assert merged.speed == 1.4
    assert merged.pitch == 0.0
    assert merged.style == "calm"


def test_merge_preferences_strips_voice_and_clears_style() -> None:
    current = VoicePreferences(voice="aura-2-thalia-en", speed=1.0, pitch=0.0, style="warm")

    merged = merge_voice_preferences(
        current,
        voice="  aura-2-apollo-en  ",
        style="none",
    )

    assert merged.voice == "aura-2-apollo-en"
    assert merged.style is None


def test_merge_preferences_rejects_empty_voice() -> None:
    current = VoicePreferences.defaults()

    merged = merge_voice_preferences(current, voice="   ")

    try:
        merged.validate()
        failed = False
    except ValueError:
        failed = True

    assert failed
