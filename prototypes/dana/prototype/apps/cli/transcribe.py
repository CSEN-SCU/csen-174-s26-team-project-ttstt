#!/usr/bin/env python3
"""
TTSTT — speech-to-text prototype (microphone → local Whisper → terminal).

Validates whether Whisper-class ASR output matches the product need before investing
in Discord, backends, or polish. Not the final UX; it only exercises the AI + capture path.
"""

from __future__ import annotations

import argparse
import os
import sys

try:
    import numpy as np
    import sounddevice as sd
    from faster_whisper import WhisperModel
except ModuleNotFoundError as e:
    sys.stderr.write(
        f"Missing dependency ({e.name!r}). The venv for this folder is probably not installed "
        f"or you are not using its Python.\n"
        f"  Current interpreter: {sys.executable}\n\n"
        "From the apps/cli directory, run:\n"
        "  python3 -m venv .venv\n"
        "  .venv/bin/python -m pip install -r requirements.txt\n"
        "  .venv/bin/python transcribe.py\n"
        "If this error is for 'faster_whisper', verify requirements were installed.\n\n"
        "Or use ./run (after chmod +x run) which always calls .venv/bin/python.\n"
    )
    raise SystemExit(1) from e

from dotenv import load_dotenv

load_dotenv()


def _record_audio(*, seconds: float, samplerate: int, device: int | None) -> np.ndarray:
    frames = max(int(seconds * samplerate), 1)
    data = sd.rec(
        frames,
        samplerate=samplerate,
        channels=1,
        dtype="float32",
        device=device,
    )
    sd.wait()
    # Keep float32 in [-1, 1], format accepted by faster-whisper.
    return np.squeeze(data).astype(np.float32)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Record from the default microphone and print a local Whisper transcription."
    )
    p.add_argument(
        "--seconds",
        type=float,
        default=5.0,
        metavar="N",
        help="How long to record (default: 5)",
    )
    p.add_argument(
        "--rate",
        type=int,
        default=16000,
        help="Sample rate in Hz (default: 16000)",
    )
    p.add_argument(
        "--device",
        type=int,
        default=None,
        metavar="INDEX",
        help="Input device index (see --list-devices)",
    )
    p.add_argument(
        "--list-devices",
        action="store_true",
        help="Print sounddevice device list and exit",
    )
    p.add_argument(
        "--model",
        default=os.environ.get("TTSTT_MODEL", "base"),
        help="Local Whisper model size/name (default: base)",
    )
    p.add_argument(
        "--compute-type",
        default=os.environ.get("TTSTT_COMPUTE_TYPE", "int8"),
        help="faster-whisper compute type (default: int8)",
    )
    p.add_argument(
        "--backend-device",
        default="auto",
        help="faster-whisper device: auto/cpu/cuda (default: auto)",
    )
    p.add_argument(
        "--language",
        default=None,
        help="Optional language hint like en, es, fr (default: auto-detect)",
    )
    args = p.parse_args()

    if args.list_devices:
        print(sd.query_devices())
        return

    print(f"Recording for {args.seconds} s… (Ctrl+C to abort)", file=sys.stderr)
    try:
        audio = _record_audio(seconds=args.seconds, samplerate=args.rate, device=args.device)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)

    print(
        f"Transcribing locally with model={args.model} device={args.backend_device}...",
        file=sys.stderr,
    )
    model = WhisperModel(
        args.model,
        device=args.backend_device,
        compute_type=args.compute_type,
    )
    segments, _info = model.transcribe(
        audio,
        language=args.language,
        vad_filter=True,
    )
    text = " ".join(segment.text.strip() for segment in segments).strip()
    print(text)


if __name__ == "__main__":
    main()
