"""Text-to-speech helpers and ElevenLabs provider integration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib import error, request

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency for local dev only
    load_dotenv = None


class TtsError(RuntimeError):
    """User-safe error raised when TTS generation fails."""


class TtsClient(Protocol):
    """Minimal provider contract expected by synthesize_text."""

    def synthesize(self, text: str, voice_prefs: dict[str, Any]) -> bytes:
        """Generate audio bytes for text + voice preferences."""


@dataclass(frozen=True)
class VoiceSettings:
    """Supported TTS settings for v1 voice controls."""

    stability: float
    speed: float


def _load_local_env_for_dev() -> None:
    if load_dotenv is not None:
        load_dotenv()


def _require_elevenlabs_api_key() -> str:
    _load_local_env_for_dev()
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise TtsError(
            "TTS provider is not configured. Set ELEVENLABS_API_KEY in server environment."
        )
    return api_key


def validate_voice_settings(voice_prefs: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize accepted voice preference fields."""
    voice_id = str(voice_prefs.get("voice", "")).strip()
    if not voice_id:
        raise ValueError("voice must be a non-empty string")

    stability = float(voice_prefs.get("stability", 0.5))
    if not 0.0 <= stability <= 1.0:
        raise ValueError("stability must be between 0.0 and 1.0")

    speed = float(voice_prefs.get("speed", 1.0))
    if not 0.7 <= speed <= 1.2:
        raise ValueError("speed must be between 0.7 and 1.2")

    return {"voice": voice_id, "stability": stability, "speed": speed}


def chunk_text_for_tts(text: str, max_chars: int = 280) -> list[str]:
    """Chunk text into space-preserving segments for provider limits."""
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        chunks.append(current)
        current = word

    chunks.append(current)
    return chunks


def synthesize_text(text: str, voice_prefs: dict[str, Any], tts_client: TtsClient) -> bytes:
    """Generate audio and map provider failures to user-safe errors."""
    try:
        if not text.strip():
            raise ValueError("text must be non-empty")
        normalized_voice_prefs = validate_voice_settings(voice_prefs)
        return tts_client.synthesize(text, normalized_voice_prefs)
    except TtsError:
        raise
    except Exception as exc:  # noqa: BLE001 - map to safe boundary error
        raise TtsError("Unable to generate speech right now. Please try again.") from exc


class ElevenLabsClient:
    """Thin ElevenLabs REST client."""

    def __init__(self, api_key: str | None = None, model_id: str = "eleven_multilingual_v2") -> None:
        self._api_key = api_key or _require_elevenlabs_api_key()
        self._model_id = model_id

    def list_voices(self) -> list[dict[str, Any]]:
        url = "https://api.elevenlabs.io/v1/voices"
        req = request.Request(
            url,
            headers={"xi-api-key": self._api_key},
            method="GET",
        )
        try:
            with request.urlopen(req, timeout=15) as resp:  # nosec B310
                payload = json.loads(resp.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise TtsError("Unable to fetch available voices right now.") from exc
        return payload.get("voices", [])

    def synthesize(self, text: str, voice_prefs: dict[str, Any]) -> bytes:
        normalized = validate_voice_settings(voice_prefs)
        voice_id = normalized["voice"]
        payload = {
            "text": text,
            "model_id": self._model_id,
            "voice_settings": {
                "stability": normalized["stability"],
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
                "speed": normalized["speed"],
            },
        }
        req = request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "xi-api-key": self._api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as resp:  # nosec B310
                return resp.read()
        except (error.URLError, TimeoutError) as exc:
            raise TtsError("Unable to generate speech right now. Please try again.") from exc


def list_voices(tts_client: ElevenLabsClient | None = None) -> list[dict[str, Any]]:
    """Return voices from ElevenLabs, using env-configured client by default."""
    client = tts_client or ElevenLabsClient()
    return client.list_voices()
