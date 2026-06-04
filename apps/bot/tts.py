"""TTS provider interface and Deepgram implementation."""

from __future__ import annotations

import inspect
import re
from typing import Mapping, Protocol

_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)


class TtsSynthesisError(RuntimeError):
    """Raised when provider synthesis fails or returns no audio."""


# Deepgram Aura speed range: https://developers.deepgram.com/docs/tts-voice-controls
DEEPGRAM_MIN_SPEED = 0.7
DEEPGRAM_MAX_SPEED = 1.5


def clamp_deepgram_speed(speed: float) -> float:
    """Clamp user speed prefs to Deepgram Aura's supported range."""
    return max(DEEPGRAM_MIN_SPEED, min(DEEPGRAM_MAX_SPEED, speed))


class TtsClient(Protocol):
    def synthesize(self, text: str, voice_prefs: Mapping[str, object]) -> bytes:
        ...


def preprocess_text_for_tts(text: str) -> str:
    """Strip URLs and collapse whitespace before synthesis."""
    without_urls = _URL_PATTERN.sub("", text)
    return " ".join(without_urls.split()).strip()


def split_text_for_progressive_tts(
    text: str,
    *,
    first_chunk_chars: int,
    max_chars: int,
) -> list[str]:
    """Split text so the first chunk is smaller for lower time-to-first-audio."""
    normalized = " ".join(text.split()).strip()
    if not normalized:
        return []

    first_chunks = chunk_text_for_tts(normalized, first_chunk_chars)
    if not first_chunks:
        return []

    first = first_chunks[0]
    if len(first_chunks) == 1:
        return first_chunks

    remainder = normalized[len(first) :].lstrip()
    if not remainder:
        return [first]

    return [first, *chunk_text_for_tts(remainder, max_chars)]


def chunk_text_for_tts(text: str, max_chars: int) -> list[str]:
    """Split text into chunks preserving order with a size limit."""
    if max_chars <= 0:
        raise ValueError("max_chars must be > 0")

    normalized = " ".join(text.split()).strip()
    if not normalized:
        return []
    if len(normalized) <= max_chars:
        return [normalized]

    chunks: list[str] = []
    current = ""
    for word in normalized.split(" "):
        if len(word) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            start = 0
            while start < len(word):
                chunks.append(word[start : start + max_chars])
                start += max_chars
            continue

        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current)
            current = word

    if current:
        chunks.append(current)
    return chunks


def synthesize_text(text: str, voice_prefs: Mapping[str, object], tts_client: TtsClient) -> bytes:
    """Map provider failures to a stable application-level error."""
    normalized = text.strip()
    if not normalized:
        raise TtsSynthesisError("text must not be empty")
    try:
        audio = tts_client.synthesize(normalized, voice_prefs)
    except TtsSynthesisError:
        raise
    except Exception as exc:
        raise TtsSynthesisError("TTS synthesis failed") from exc

    if not audio:
        raise TtsSynthesisError("TTS synthesis returned empty audio")
    return audio


class DeepgramTtsClient:
    """Deepgram-backed TTS client that returns WAV bytes."""

    def __init__(self, api_key: str, default_voice: str = "aura-2-thalia-en") -> None:
        if not api_key:
            raise ValueError("Deepgram API key is required for TTS")
        self._api_key = api_key
        self._default_voice = default_voice
        self._client = None

    def synthesize(self, text: str, voice_prefs: Mapping[str, object]) -> bytes:
        if not text.strip():
            raise TtsSynthesisError("text must not be empty")

        client = self._get_client()
        voice = str(voice_prefs.get("voice") or self._default_voice)

        options: dict[str, object] = {
            "model": voice,
            "text": text,
            "encoding": "linear16",
            "container": "wav",
        }
        speed = voice_prefs.get("speed")
        pitch = voice_prefs.get("pitch")
        if speed is not None:
            options["speed"] = clamp_deepgram_speed(float(speed))
        if pitch is not None:
            options["pitch"] = pitch

        generate_fn = client.speak.v1.audio.generate
        accepted_keys = set(inspect.signature(generate_fn).parameters.keys())
        filtered_options = {key: value for key, value in options.items() if key in accepted_keys}
        try:
            response = generate_fn(**filtered_options)
            return _extract_audio_bytes(response)
        except TtsSynthesisError:
            raise
        except Exception as exc:
            raise TtsSynthesisError("Deepgram TTS request failed") from exc

    def _get_client(self) -> object:
        if self._client is None:
            try:
                from deepgram import DeepgramClient
            except Exception as exc:  # pragma: no cover - depends on environment
                raise TtsSynthesisError("deepgram-sdk is not installed") from exc
            self._client = DeepgramClient(api_key=self._api_key)
        return self._client


def _extract_audio_bytes(response: object) -> bytes:
    if hasattr(response, "__iter__") and not isinstance(response, (str, bytes, bytearray, dict)):
        collected = bytearray()
        for chunk in response:  # type: ignore[operator]
            if isinstance(chunk, (bytes, bytearray)):
                collected.extend(chunk)
                continue
            if isinstance(chunk, dict):
                for key in ("data", "audio", "bytes"):
                    value = chunk.get(key)
                    if isinstance(value, (bytes, bytearray)):
                        collected.extend(value)
                        break
                continue
            for key in ("data", "audio", "stream"):
                value = getattr(chunk, key, None)
                if isinstance(value, (bytes, bytearray)):
                    collected.extend(value)
                    break
            getvalue = getattr(chunk, "getvalue", None)
            if callable(getvalue):
                maybe_bytes = getvalue()
                if isinstance(maybe_bytes, (bytes, bytearray)):
                    collected.extend(maybe_bytes)
        if collected:
            return bytes(collected)

    for attr in ("stream", "audio", "data"):
        value = getattr(response, attr, None)
        if value is None:
            continue
        if isinstance(value, (bytes, bytearray)):
            return bytes(value)
        getvalue = getattr(value, "getvalue", None)
        if callable(getvalue):
            maybe_bytes = getvalue()
            if isinstance(maybe_bytes, (bytes, bytearray)):
                return bytes(maybe_bytes)
    raise TtsSynthesisError("Deepgram response did not include audio bytes")
