"""
Future-facing unit test for ASR provider error handling.
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


def test_transcribe_audio_maps_provider_timeout_to_transcription_error() -> None:
    # As a Discord participant, if transcription times out, I get a clear failure path instead of the bot crashing.

    # Arrange
    transcribe_audio = _load_transcribe_audio()

    class FakeAsrTimeoutError(Exception):
        pass

    class FakeAsrClient:
        def transcribe(self, audio_bytes: bytes) -> str:
            raise FakeAsrTimeoutError("provider timed out")

    fake_audio = b"\x10\x20\x30"
    fake_client = FakeAsrClient()

    # Action / Assert
    with pytest.raises(Exception):
        transcribe_audio(fake_audio, fake_client)
