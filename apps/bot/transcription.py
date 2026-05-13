"""Speech-to-text helpers for bot workflows."""

from __future__ import annotations

from typing import Protocol


class AsrClient(Protocol):
    """Minimal ASR client contract expected by transcription helpers."""

    def transcribe(self, audio_bytes: bytes) -> str:
        """Return recognized text for the given audio bytes."""


class AsrTranscriptionError(RuntimeError):
    """Raised when provider transcription fails."""


def transcribe_audio(audio_bytes: bytes, asr_client: AsrClient) -> str:
    """Convert audio bytes to text using an injected ASR client."""
    return asr_client.transcribe(audio_bytes).strip()


class DeepgramAsrClient:
    """Deepgram-backed ASR client using the pre-recorded transcription API."""

    def __init__(self, api_key: str, model: str = "nova-2") -> None:
        if not api_key:
            raise ValueError("Deepgram API key is required for ASR")
        self._api_key = api_key
        self._model = model
        self._client = None

    def transcribe(self, audio_bytes: bytes) -> str:
        """Send WAV audio bytes to Deepgram and return the transcript string."""
        client = self._get_client()
        try:
            from deepgram import PrerecordedOptions
        except Exception as exc:
            raise AsrTranscriptionError("deepgram-sdk is not installed") from exc

        source = {"buffer": audio_bytes, "mimetype": "audio/wav"}
        options = PrerecordedOptions(model=self._model, smart_format=True)
        try:
            response = client.listen.rest.v("1").transcribe_file(source, options)
            return response.results.channels[0].alternatives[0].transcript
        except AsrTranscriptionError:
            raise
        except Exception as exc:
            raise AsrTranscriptionError("Deepgram ASR request failed") from exc

    def _get_client(self) -> object:
        if self._client is None:
            try:
                from deepgram import DeepgramClient
            except Exception as exc:
                raise AsrTranscriptionError("deepgram-sdk is not installed") from exc
            self._client = DeepgramClient(api_key=self._api_key)
        return self._client
