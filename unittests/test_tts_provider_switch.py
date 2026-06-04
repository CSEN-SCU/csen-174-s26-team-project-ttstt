from __future__ import annotations

from apps.bot.voice_preferences import (
    TtsProvider,
    VoicePreferences,
    apply_tts_provider_switch,
    default_voice_for_provider,
    is_deepgram_voice_id,
)


def test_is_deepgram_voice_id() -> None:
    assert is_deepgram_voice_id("aura-2-thalia-en")
    assert not is_deepgram_voice_id("en_US-lessac-medium")


def test_apply_tts_provider_switch_resets_voice_for_piper() -> None:
    current = VoicePreferences(
        voice="aura-2-thalia-en",
        speed=1.1,
        pitch=-2.0,
        tts_provider=TtsProvider.DEEPGRAM,
    )

    switched = apply_tts_provider_switch(current, TtsProvider.PIPER)

    assert switched.tts_provider is TtsProvider.PIPER
    assert switched.voice == default_voice_for_provider(TtsProvider.PIPER)
    assert switched.speed == 1.1
    assert switched.pitch == -2.0


def test_apply_tts_provider_switch_resets_voice_for_deepgram() -> None:
    current = VoicePreferences(
        voice="en_US-lessac-medium",
        speed=1.0,
        pitch=0.0,
        tts_provider=TtsProvider.PIPER,
    )

    switched = apply_tts_provider_switch(current, TtsProvider.DEEPGRAM)

    assert switched.tts_provider is TtsProvider.DEEPGRAM
    assert switched.voice == default_voice_for_provider(TtsProvider.DEEPGRAM)


def test_apply_tts_provider_switch_noop_when_unchanged() -> None:
    current = VoicePreferences.defaults()
    assert apply_tts_provider_switch(current, TtsProvider.DEEPGRAM) is current
