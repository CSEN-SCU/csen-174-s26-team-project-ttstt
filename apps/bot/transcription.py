"""Speech-to-text helpers for bot workflows."""

from __future__ import annotations

import json
import sys
import time
from typing import Protocol

_DEBUG_LOG_PATH = "/home/terni/Documents/GitHub/csen-174-s26-team-project-ttstt/.cursor/debug-7b5ea9.log"


def _agent_log(*, hypothesis_id: str, location: str, message: str, data: dict[str, object]) -> None:
    # #region agent log
    try:
        payload = {
            "sessionId": "7b5ea9",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(_DEBUG_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
    except OSError:
        pass
    # #endregion


class AsrClient(Protocol):
    """Minimal ASR client contract expected by transcription helpers."""

    def transcribe(self, audio_bytes: bytes) -> str:
        """Return recognized text for the given audio bytes."""


class AsrTranscriptionError(RuntimeError):
    """Raised when provider transcription fails."""


def transcribe_audio(audio_bytes: bytes, asr_client: AsrClient) -> str:
    """Convert audio bytes to text using an injected ASR client."""
    return asr_client.transcribe(audio_bytes).strip()


def _extract_transcript_from_response(response: object) -> tuple[str, list[str]]:
    """Collect transcript text from all channels/alternatives in a Deepgram response."""

    channels = getattr(getattr(response, "results", None), "channels", None)
    if not channels:
        return "", []

    per_channel: list[str] = []
    for channel in channels:
        alternatives = getattr(channel, "alternatives", None) or []
        # Only take the best (first) alternative; Deepgram returns alternatives best-first.
        # Taking all of them would concatenate n-best hypotheses into garbled output.
        best = alternatives[:1]
        for alternative in best:
            text = (getattr(alternative, "transcript", "") or "").strip()
            if text:
                per_channel.append(text)
    merged = " ".join(per_channel).strip()
    return merged, per_channel


class DeepgramAsrClient:
    """Deepgram-backed ASR client using the pre-recorded transcription API (SDK v4)."""

    def __init__(self, api_key: str, model: str = "nova-3") -> None:
        if not api_key:
            raise ValueError("Deepgram API key is required for ASR")
        self._api_key = api_key
        self._model = model
        self._client = None

    def transcribe(self, audio_bytes: bytes) -> str:
        """Send WAV audio bytes to Deepgram and return the transcript string."""
        # #region agent log
        _agent_log(
            hypothesis_id="H1",
            location="transcription.py:transcribe:entry",
            message="ASR transcribe called",
            data={"python": sys.executable, "audio_bytes": len(audio_bytes), "model": self._model},
        )
        # #endregion
        if not audio_bytes:
            return ""

        client = self._get_client()
        try:
            response = client.listen.v1.media.transcribe_file(  # type: ignore[union-attr]
                request=audio_bytes,
                model=self._model,
                smart_format=True,
                punctuate=True,
                language="en",
            )
        except AsrTranscriptionError:
            raise
        except Exception as exc:
            # #region agent log
            _agent_log(
                hypothesis_id="H4",
                location="transcription.py:transcribe:api_error",
                message="Deepgram API call failed",
                data={"exc_type": type(exc).__name__, "exc_msg": str(exc)[:200]},
            )
            # #endregion
            raise AsrTranscriptionError("Deepgram ASR request failed") from exc

        transcript, per_channel = _extract_transcript_from_response(response)
        channel_count = len(getattr(getattr(response, "results", None), "channels", None) or [])

        # Build detailed per-channel diagnostic data
        raw_channels = getattr(getattr(response, "results", None), "channels", None) or []
        channel_details: list[dict[str, object]] = []
        for ch_idx, channel in enumerate(raw_channels):
            alts = getattr(channel, "alternatives", None) or []
            alt_details: list[dict[str, object]] = []
            for alt in alts:
                words = getattr(alt, "words", None) or []
                word_list = [
                    {
                        "word": getattr(w, "word", None),
                        "confidence": getattr(w, "confidence", None),
                        "start": getattr(w, "start", None),
                        "end": getattr(w, "end", None),
                    }
                    for w in words[:10]  # cap at 10 words to keep log manageable
                ]
                alt_details.append({
                    "transcript": getattr(alt, "transcript", ""),
                    "confidence": getattr(alt, "confidence", None),
                    "words_count": len(words),
                    "words_sample": word_list,
                })
            channel_details.append({"ch_idx": ch_idx, "alternatives": alt_details})

        metadata = getattr(response, "metadata", None)
        # #region agent log
        _agent_log(
            hypothesis_id="H2" if transcript else "H5",
            location="transcription.py:transcribe:result",
            message="ASR transcribe completed",
            data={
                "transcript_len": len(transcript),
                "channel_count": channel_count,
                "per_channel_lens": [len(part) for part in per_channel],
                "channel_details": channel_details,
                "request_id": getattr(metadata, "request_id", None),
                "duration": getattr(metadata, "duration", None),
                "channels_meta": getattr(metadata, "channels", None),
            },
        )
        # #endregion
        return transcript

    def _get_client(self) -> object:
        if self._client is None:
            try:
                from deepgram import DeepgramClient
            except ImportError as exc:
                # #region agent log
                _agent_log(
                    hypothesis_id="H1",
                    location="transcription.py:_get_client:import_error",
                    message="deepgram package import failed",
                    data={"exc_type": type(exc).__name__, "exc_msg": str(exc)},
                )
                # #endregion
                raise AsrTranscriptionError("deepgram-sdk is not installed") from exc
            except Exception as exc:
                # #region agent log
                _agent_log(
                    hypothesis_id="H3",
                    location="transcription.py:_get_client:unexpected_import",
                    message="unexpected error importing deepgram",
                    data={"exc_type": type(exc).__name__, "exc_msg": str(exc)},
                )
                # #endregion
                raise AsrTranscriptionError(f"Failed to load deepgram-sdk: {exc}") from exc
            self._client = DeepgramClient(api_key=self._api_key)
            # #region agent log
            _agent_log(
                hypothesis_id="H2",
                location="transcription.py:_get_client:ready",
                message="DeepgramClient constructed",
                data={"sdk_v4": True},
            )
            # #endregion
        return self._client
