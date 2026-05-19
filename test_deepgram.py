#!/usr/bin/env python3
"""Quick sanity-check: send a WAV file through the same Deepgram path the bot uses."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

wav_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("stt_debug_audio/wha_happun.wav")
if not wav_path.exists():
    print(f"File not found: {wav_path}")
    sys.exit(1)

audio_bytes = wav_path.read_bytes()
print(f"Sending {wav_path.name} ({len(audio_bytes):,} bytes) to Deepgram...")

from apps.bot.transcription import DeepgramAsrClient

api_key = os.environ["DEEPGRAM_API_KEY"]
client = DeepgramAsrClient(api_key=api_key)
result = client.transcribe(audio_bytes)

if result:
    print(f"Transcript: {result!r}")
else:
    print("Empty transcript — Deepgram returned nothing.")
