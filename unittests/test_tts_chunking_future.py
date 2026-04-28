"""
Future-facing unit test for TTS chunking of long text messages.
"""

from __future__ import annotations

import importlib
from typing import Callable

import pytest


MODULE_PATH = "apps.bot.tts"
FUNCTION_NAME = "chunk_text_for_tts"


def _load_chunk_text_for_tts() -> Callable:
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


def test_chunk_text_for_tts_preserves_order_and_length_limit() -> None:
    # As a voice-channel listener, long messages are split safely and played in the original order.

    # Arrange
    chunk_text_for_tts = _load_chunk_text_for_tts()
    long_text = "one two three four five six seven eight nine ten"
    max_chars = 12

    # Action
    chunks = chunk_text_for_tts(long_text, max_chars)

    # Assert
    assert isinstance(chunks, list)
    assert chunks
    assert all(isinstance(chunk, str) for chunk in chunks)
    assert all(len(chunk) <= max_chars for chunk in chunks)
    assert " ".join(chunks).replace("  ", " ").strip() == long_text
