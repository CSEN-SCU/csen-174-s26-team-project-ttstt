"""
Optional live integration test for Deepgram TTS.

This test makes a real network call and is opt-in:
- Set RUN_LIVE_DEEPGRAM_TEST=1
- Set DEEPGRAM_API_KEY in environment (or .env loaded by your shell)
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from apps.bot.tts import DeepgramTtsClient, synthesize_text


def test_deepgram_live_tts_returns_wav_file(tmp_path: Path) -> None:
    if os.getenv("RUN_LIVE_DEEPGRAM_TEST") != "1":
        pytest.skip("Set RUN_LIVE_DEEPGRAM_TEST=1 to run live Deepgram TTS integration test.")

    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        pytest.skip("DEEPGRAM_API_KEY is not set.")

    client = DeepgramTtsClient(api_key=api_key)
    audio_bytes = synthesize_text(
        text="Hello from TTSTT live Deepgram test.",
        voice_prefs={"voice": "aura-2-thalia-en", "speed": 1.0},
        tts_client=client,
    )

    output_file = tmp_path / "deepgram_live_test.wav"
    output_file.write_bytes(audio_bytes)

    assert output_file.exists()
    assert output_file.stat().st_size > 44  # larger than bare WAV header
    assert audio_bytes[:4] == b"RIFF"
    assert audio_bytes[8:12] == b"WAVE"
