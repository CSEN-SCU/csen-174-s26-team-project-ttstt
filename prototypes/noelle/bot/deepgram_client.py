"""Deepgram transcription client wrappers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

from deepgram import DeepgramClient


@dataclass(slots=True)
class TranscriptResult:
    """Represents one transcription result from Deepgram."""

    text: str
    confidence: float


class DeepgramTranscriber:
    """Async-friendly wrapper around the Deepgram Python SDK."""

    def __init__(self, api_key: str, model: str = "nova-3", min_confidence: float = 0.5) -> None:
        self._client = DeepgramClient(api_key=api_key)
        self._model = model
        self._min_confidence = min_confidence

    async def transcribe_wav(self, wav_bytes: bytes) -> Optional[TranscriptResult]:
        """Transcribe WAV bytes and return a filtered transcript."""

        if not wav_bytes:
            return None

        response = await asyncio.to_thread(
            self._client.listen.v1.media.transcribe_file,
            request=wav_bytes,
            model=self._model,
        )

        channels = getattr(getattr(response, "results", None), "channels", None)
        if not channels:
            return None

        alternatives = getattr(channels[0], "alternatives", None)
        if not alternatives:
            return None

        best = alternatives[0]
        transcript = (getattr(best, "transcript", "") or "").strip()
        confidence = float(getattr(best, "confidence", 0.0) or 0.0)

        if not transcript:
            return None
        if confidence < self._min_confidence:
            return None

        return TranscriptResult(text=transcript, confidence=confidence)
