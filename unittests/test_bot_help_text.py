from __future__ import annotations

from apps.bot.main import _build_help_text


def test_build_help_text_includes_all_commands_and_key_options() -> None:
    text = _build_help_text()

    assert "/join" in text
    assert "/leave" in text
    assert "/status" in text
    assert "/tts_listen_user" in text
    assert "/tts_stop_listening" in text
    assert "/tts_voice_set" in text
    assert "/tts_voice_show" in text
    assert "/tts_voice_reset" in text
    assert "/help" in text

    assert "speed: 0.5 to 2.0" in text
    assert "pitch: -20 to 20" in text
    assert "control text channel" in text
