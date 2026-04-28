"""
Future-facing unit test for speech-to-text behavior described in README.md.

README expectation: voice input is converted into text via ASR.
This test defines a simple contract for that behavior and will be skipped
until the target implementation module exists.
"""

from __future__ import annotations

import importlib
from typing import Callable

import pytest


MODULE_PATH = "apps.bot.transcription"
FUNCTION_NAME = "transcribe_audio"


def _load_transcribe_audio() -> Callable:
    """
    Load the future transcription function once implementation exists.
    """
    try:
        module = importlib.import_module(MODULE_PATH)
    except ModuleNotFoundError:
        pytest.skip(
            f"{MODULE_PATH!r} does not exist yet. "
            "Unskip this test after speech-to-text implementation is added."
        )

    if not hasattr(module, FUNCTION_NAME):
        pytest.skip(
            f"{MODULE_PATH!r} exists, but {FUNCTION_NAME!r} is not implemented yet."
        )

    return getattr(module, FUNCTION_NAME)


def test_transcribe_audio_returns_text_from_asr_output() -> None:
    # As a Discord participant, my spoken words are transcribed into text so everyone can follow the conversation.

    # Arrange
    transcribe_audio = _load_transcribe_audio()

    class FakeAsrClient:
        def __init__(self) -> None:
            self.called_with: bytes | None = None

        def transcribe(self, audio_bytes: bytes) -> str:
            self.called_with = audio_bytes
            return "hello from speech"

    fake_client = FakeAsrClient()
    fake_audio = b"\x00\x01\x02\x03"

    # Action
    result = transcribe_audio(fake_audio, fake_client)

    # Assert
    assert fake_client.called_with == fake_audio
    assert isinstance(result, str)
    assert result == "hello from speech"
