# TTSTT Overlay Prototype — Diego

A real-time overlay that bridges voice and text communication. Simulates two
users on a single machine: speak into the mic to produce transcribed messages,
or type a reply that is automatically read aloud.

## Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+ with pip
- **ffmpeg** on your PATH (required by faster-whisper)

### 1. Backend

```bash
cd prototypes/diego/backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python main.py            # starts on :8000
```

### 2. Frontend

```bash
cd prototypes/diego/frontend
npm install
npm run dev               # starts on :5173, proxies /api → :8000
```

### 3. Open

Navigate to <http://localhost:5173>. You'll see an intro screen that explains
the app. Press **Start Demo** to enter the overlay view.

## How to Use

| Action | What happens |
|--------|-------------|
| **Hold the mic button** (bottom-left) and speak | Audio is sent to the backend, transcribed via Whisper, and appears in the chat feed as a "Voice User" message. |
| **Press `/`** and type a message, then Enter | The message appears in the chat feed as "You" and is automatically read aloud via edge-tts. |
| **Press `Escape`** | Blurs the text input back to the overlay. |

## Environment Variables (optional)

Copy `.env.example` to `.env` in the `prototypes/diego/` directory:

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `base` | faster-whisper model size (`tiny`, `base`, `small`, `medium`, `large-v3`) |
| `TTS_VOICE` | `en-US-AriaNeural` | Default edge-tts voice |
| `BACKEND_PORT` | `8000` | Port for the FastAPI server |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite 6, Tailwind CSS v4 |
| Backend | FastAPI, faster-whisper (local Whisper), edge-tts |
| Fonts | Sora (headings), IBM Plex Mono (overlay UI) |
