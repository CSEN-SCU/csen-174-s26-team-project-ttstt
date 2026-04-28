"""
Future-facing unit test for applying per-user TTS voice settings.
"""

from __future__ import annotations

import importlib
from typing import Callable

import pytest


MODULE_PATH = "apps.bot.tts"
FUNCTION_NAME = "synthesize_text"


def _load_synthesize_text() -> Callable:
    try:
        module = importlib.import_module(MODULE_PATH)
    except ModuleNotFoundError:
        pytest.skip(
            f"{MODULE_PATH!r} does not exist yet. "
            "Unskip this test after TTS implementation is added."
        )

    if not hasattr(module, FUNCTION_NAME):
        pytest.skip(
            f"{MODULE_PATH!r} exists, but {FUNCTION_NAME!r} is not implemented yet."
        )

    return getattr(module, FUNCTION_NAME)


def test_synthesize_text_applies_user_voice_preferences() -> None:
    # As a text-first user, my selected synthetic voice settings are applied so my messages sound like my chosen style.

    # Arrange
    synthesize_text = _load_synthesize_text()

    class FakeTtsClient:
        def __init__(self) -> None:
            self.last_text: str | None = None
            self.last_voice_prefs: dict | None = None

        def synthesize(self, text: str, voice_prefs: dict) -> bytes:
            self.last_text = text
            self.last_voice_prefs = voice_prefs
            return b"audio-bytes"

    fake_client = FakeTtsClient()
    text = "hello voice channel"
    voice_prefs = {"voice": "calm", "speed": 1.1, "pitch": -1}

    # Action
    audio = synthesize_text(text, voice_prefs, fake_client)

    # Assert
    assert fake_client.last_text == text
    assert fake_client.last_voice_prefs == voice_prefs
    assert isinstance(audio, bytes)
    assert audio == b"audio-bytes"
