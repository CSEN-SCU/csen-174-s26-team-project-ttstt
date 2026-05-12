"""Provider-agnostic text-to-speech helpers for the Discord bot.

This module is the seam between bot orchestration and any specific TTS vendor.
Concrete clients (e.g. ElevenLabs) implement the ``TtsClient`` protocol; bot
code only depends on the small surface here.
"""

from __future__ import annotations

import os
from typing import Protocol


class TtsClient(Protocol):
    """Minimal TTS provider contract used by the bot."""

    def synthesize(self, text: str, voice_prefs: dict) -> bytes:
        """Return synthesized audio bytes for ``text`` shaped by ``voice_prefs``."""


def synthesize_text(text: str, voice_prefs: dict, tts_client: TtsClient) -> bytes:
    """Synthesize ``text`` using ``tts_client`` and the given voice preferences.

    Provider errors are intentionally propagated so callers can decide how to
    surface them (e.g. an ephemeral Discord reply vs. a structured log entry).
    """
    return tts_client.synthesize(text, voice_prefs)


def chunk_text_for_tts(text: str, max_chars: int) -> list[str]:
    """Split ``text`` into ordered chunks where each chunk fits ``max_chars``.

    Chunks break on whitespace where possible so words stay intact. Very long
    individual words that exceed ``max_chars`` are hard-split as a last resort
    so the size guarantee always holds.
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be positive.")

    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    current = ""
    for word in words:
        # Hard-split words that are larger than the per-chunk budget.
        while len(word) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(word[:max_chars])
            word = word[max_chars:]

        if not current:
            current = word
            continue

        candidate = f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current)
            current = word

    if current:
        chunks.append(current)

    return chunks


def load_default_voice_prefs_from_env() -> dict:
    """Read default voice preferences from environment variables.

    The returned dict is the canonical shape expected by ``TtsClient``
    implementations. Optional numeric fields are only included when set so
    provider defaults still apply when an operator leaves them blank.
    """
    prefs: dict = {}

    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    if voice_id:
        prefs["voice_id"] = voice_id

    model_id = os.getenv("ELEVENLABS_MODEL_ID")
    if model_id:
        prefs["model_id"] = model_id

    stability = _optional_float("ELEVENLABS_STABILITY")
    if stability is not None:
        prefs["stability"] = stability

    similarity_boost = _optional_float("ELEVENLABS_SIMILARITY_BOOST")
    if similarity_boost is not None:
        prefs["similarity_boost"] = similarity_boost

    style = _optional_float("ELEVENLABS_STYLE")
    if style is not None:
        prefs["style"] = style

    speaker_boost = os.getenv("ELEVENLABS_USE_SPEAKER_BOOST")
    if speaker_boost is not None and speaker_boost.strip():
        prefs["use_speaker_boost"] = speaker_boost.strip().lower() in {"1", "true", "yes", "on"}

    return prefs


def _optional_float(env_name: str) -> float | None:
    raw = os.getenv(env_name)
    if raw is None or not raw.strip():
        return None
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{env_name} must be a number when provided.") from exc
