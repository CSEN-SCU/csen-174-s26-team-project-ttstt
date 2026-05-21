"""Unit tests for /tts_voice_set wiring (no discord import)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = REPO_ROOT / "apps" / "bot" / "main.py"
VOICE_PREFS_PY = REPO_ROOT / "apps" / "bot" / "voice_preferences.py"


def test_tts_voice_set_registered_in_setup_hook() -> None:
    text = MAIN_PY.read_text(encoding="utf-8")
    assert "self.tree.add_command(tts_voice_set)" in text
    assert '@app_commands.command(name="tts_voice_set"' in text


def test_tts_voice_set_has_voice_autocomplete() -> None:
    text = MAIN_PY.read_text(encoding="utf-8")
    assert '@tts_voice_set.autocomplete("voice")' in text
    assert "FEATURED_AURA2_VOICES" in text


def test_merge_voice_preferences_lives_in_voice_preferences_module() -> None:
    text = VOICE_PREFS_PY.read_text(encoding="utf-8")
    assert "def merge_voice_preferences(" in text
    assert "FEATURED_AURA2_VOICES" in text
