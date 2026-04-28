"""
Future-facing unit test for silence handling in speech-to-text flow.
"""

from __future__ import annotations

import importlib
from typing import Callable

import pytest


MODULE_PATH = "apps.bot.transcription"
FUNCTION_NAME = "transcribe_audio"


def _load_transcribe_audio() -> Callable:
    try:
        module = importlib.import_module(MODULE_PATH)
    except ModuleNotFoundError:
        pytest.skip(
            f"{MODULE_PATH!r} does not exist yet. "
            "Unskip this test after transcription implementation is added."
        )

    if not hasattr(module, FUNCTION_NAME):
        pytest.skip(
            f"{MODULE_PATH!r} exists, but {FUNCTION_NAME!r} is not implemented yet."
        )

    return getattr(module, FUNCTION_NAME)


def test_transcribe_audio_returns_empty_text_for_silence() -> None:
    # As a Discord participant, silent audio does not post misleading words into chat.

    # Arrange
    transcribe_audio = _load_transcribe_audio()

    class FakeAsrClient:
        def transcribe(self, audio_bytes: bytes) -> str:
            return ""

    fake_silence_audio = b"\x00" * 64
    fake_client = FakeAsrClient()

    # Action
    result = transcribe_audio(fake_silence_audio, fake_client)

    # Assert
    assert isinstance(result, str)
    assert result == ""
