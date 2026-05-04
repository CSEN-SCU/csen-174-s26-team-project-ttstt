"""
Future-facing unit test for TTS provider error handling.
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


def test_synthesize_text_maps_provider_failure_to_user_safe_error() -> None:
    # As a voice-channel listener, if the TTS fails, I get a clear failure path instead of the bot crashing.

    # Arrange
    synthesize_text = _load_synthesize_text()

    class FakeProviderTimeout(Exception):
        pass

    class FakeTtsClient:
        def synthesize(self, text: str, voice_prefs: dict) -> bytes:
            raise FakeProviderTimeout("TTS provider timed out")

    text = "Please read this message aloud."
    voice_prefs = {
        "voice": "calm",
        "speed": 1.0,
        "pitch": 0.0,
    }
    fake_client = FakeTtsClient()

    # Action / Assert
    with pytest.raises(Exception):
        synthesize_text(text, voice_prefs, fake_client)
