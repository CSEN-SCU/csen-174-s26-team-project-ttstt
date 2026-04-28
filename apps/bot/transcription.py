"""Speech-to-text helpers for bot workflows."""

from __future__ import annotations

from typing import Protocol


class AsrClient(Protocol):
    """Minimal ASR client contract expected by transcription helpers."""

    def transcribe(self, audio_bytes: bytes) -> str:
        """Return recognized text for the given audio bytes."""


def transcribe_audio(audio_bytes: bytes, asr_client: AsrClient) -> str:
    """
    Convert audio bytes to text using an injected ASR client.

    Keeping this function dependency-injected makes it simple to test and
    keeps model/provider details outside core bot flow logic.
    """
    return asr_client.transcribe(audio_bytes).strip()
