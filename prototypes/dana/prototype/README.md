# TTSTT (Text To Speech To Text)

By: Noelle Evanich, Diego Silva, Dana Steinke

**CSEN 174 — planning / design phase.** This repository documents the **intended** product. A small **STT prototype** lives under [`apps/cli/`](apps/cli/) to try Whisper on live microphone input (see that folder’s `requirements.txt`).

## Intended product (summary)

A **Discord bot** plus a **backend service** so participants can:

- Turn **voice** into **text** in a server (via **automatic speech recognition**, e.g. Whisper-class APIs).
- Hear **text chat** read aloud in **voice channels** (**neural text-to-speech**, e.g. Piper-style models from Hugging Face), with per-user voice and prosody settings.
- Apply optional **server-side audio post-processing** (e.g. ffmpeg: pitch/tempo, default loudness normalization).

The course-facing **product vision** and rationale are in **[`docs/product-vision.md`](docs/product-vision.md)**.

## What is in this repo right now

| Location | Contents |
|----------|----------|
| [`apps/cli/`](apps/cli) | **Prototype:** command-line mic → **local Whisper (faster-whisper)** → transcript printed to the terminal |
| [`docs/`](docs) | Product vision, learning journal, and other course artifacts |
| [`infra/`](infra) | Example **Docker Compose** for **Postgres** (for when the backend is implemented) — optional local dev database |

**Not included yet:** A Discord bot, full backend API, CI workflows, or deployment automation beyond this local STT sketch.

### Run the STT prototype (CLI)

Work **inside** [`apps/cli/`](apps/cli) so the virtualenv path is correct. Use the venv’s Python explicitly (avoid `python transcribe.py`, which often picks up the system interpreter):

```sh
cd apps/cli
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# optional: copy .env.example → .env to set TTSTT_MODEL / TTSTT_COMPUTE_TYPE defaults
.venv/bin/python transcribe.py
```

Optional: `chmod +x run && ./run` runs `.venv/bin/python transcribe.py` for you.

**Fish shell:** do not `source .venv/bin/activate` (use `.venv/bin/activate.fish` if you want activation), or skip activation and only use `.venv/bin/python` as above.

The first run may download the selected Whisper model weights.

On many Linux systems, install PortAudio dev headers before `pip install` so `sounddevice` can build (for example on Debian/Ubuntu: `portaudio19-dev`).

## For course staff

- **Scope:** Software engineering process (vision, architecture, testing, and deployment **to be documented** as the quarter progresses).  
- **AI:** The design centers on **speech recognition** and **speech synthesis** as the core capabilities (vendor-agnostic in documentation).  
- **Status:** **Pre-implementation** — use `docs/` and team process artifacts to assess planning; do not expect a runnable demo from this repository state alone.
