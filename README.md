# TTSTT (Text To Speech To Text)

By: Noelle Evanich

**CSEN 174 — planning / design phase.** This repository documents the **intended** product; **there is no application code here yet** (the `apps/` tree has been removed until implementation begins).

## Intended product (summary)

A **Discord bot** plus a **backend service** so participants can:

- Turn **voice** into **text** in a server (via **automatic speech recognition**, e.g. Whisper-class APIs).
- Hear **text chat** read aloud in **voice channels** (**neural text-to-speech**, e.g. Piper-style models from Hugging Face), with per-user voice and prosody settings.
- Apply optional **server-side audio post-processing** (e.g. ffmpeg: pitch/tempo, default loudness normalization).

The course-facing **product vision** and rationale are in **[`docs/product-vision.md`](docs/product-vision.md)**.

## What is in this repo right now

| Location | Contents |
|----------|----------|
| [`docs/`](docs) | Product vision, learning journal, and other course artifacts |
| [`infra/`](infra) | Example **Docker Compose** for **Postgres** (for when the backend is implemented) — optional local dev database |

**Not included yet:** Python packages for a Discord bot or API, CI workflows, or deployment—those will land under a future `apps/` (or similar) layout once the team moves from planning to implementation.

## For course staff

- **Scope:** Software engineering process (vision, architecture, testing, and deployment **to be documented** as the quarter progresses).  
- **AI:** The design centers on **speech recognition** and **speech synthesis** as the core capabilities (vendor-agnostic in documentation).  
- **Status:** **Pre-implementation** — use `docs/` and team process artifacts to assess planning; do not expect a runnable demo from this repository state alone.
