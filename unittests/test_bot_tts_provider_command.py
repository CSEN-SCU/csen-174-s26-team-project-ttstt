"""Unit tests for /tts_provider_set wiring (no discord import)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = REPO_ROOT / "apps" / "bot" / "main.py"


def test_tts_provider_set_registered_in_setup_hook() -> None:
    text = MAIN_PY.read_text(encoding="utf-8")
    assert "self.tree.add_command(tts_provider_set)" in text
    assert '@app_commands.command(\n    name="tts_provider_set"' in text or 'name="tts_provider_set"' in text


def test_relay_bot_resolves_deepgram_and_piper_clients() -> None:
    text = MAIN_PY.read_text(encoding="utf-8")
    assert "def _resolve_tts_client(self, provider: TtsProvider)" in text
    assert "tts_deepgram" in text
    assert "tts_piper" in text
