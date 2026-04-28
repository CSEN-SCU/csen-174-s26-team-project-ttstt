"""
Future-facing unit test for bidirectional bridge routing behavior.
"""

from __future__ import annotations

import importlib
from typing import Callable

import pytest


MODULE_PATH = "apps.bot.bridge"
FUNCTION_NAME = "route_event"


def _load_route_event() -> Callable:
    try:
        module = importlib.import_module(MODULE_PATH)
    except ModuleNotFoundError:
        pytest.skip(
            f"{MODULE_PATH!r} does not exist yet. "
            "Unskip this test after bridge routing implementation is added."
        )

    if not hasattr(module, FUNCTION_NAME):
        pytest.skip(
            f"{MODULE_PATH!r} exists, but {FUNCTION_NAME!r} is not implemented yet."
        )

    return getattr(module, FUNCTION_NAME)


def test_route_event_sends_voice_events_to_transcription_pipeline() -> None:
    # As a hard-of-hearing participant, voice events are routed into transcription so spoken content appears in text.

    # Arrange
    route_event = _load_route_event()

    class FakeRouterContext:
        def __init__(self) -> None:
            self.transcription_calls: list[bytes] = []

        def send_to_transcription(self, audio_bytes: bytes) -> None:
            self.transcription_calls.append(audio_bytes)

    context = FakeRouterContext()
    voice_event = {"type": "voice_audio", "audio_bytes": b"\x01\x02\x03"}

    # Action
    route_event(voice_event, context)

    # Assert
    assert context.transcription_calls == [b"\x01\x02\x03"]
