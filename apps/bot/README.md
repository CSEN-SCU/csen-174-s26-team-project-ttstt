# TTSTT Bot

A deployable Discord bot that bridges text and voice channels using
**ElevenLabs** neural text-to-speech. The bot can join a voice channel and
either read individual messages on demand (`/say`) or auto-read everything
posted in the channel where you ran `/join` (`/relay on`).

Speech-to-text (the inbound side of TTSTT) is not wired into this skeleton
yet; it lives behind the same `apps/bot/transcription.py` seam and will be
filled in by a separate workstream.

## Commands

| Command | What it does |
|---|---|
| `/join` | Join the voice channel you are currently in and remember the text channel you ran `/join` from. |
| `/leave` | Disconnect from voice in the current server. |
| `/status` | Show the active voice channel, bound text channel, and auto-relay state. |
| `/say message:<text>` | Synthesize `<text>` with ElevenLabs and play it in the voice channel. |
| `/relay state:on\|off` | Toggle automatic reading of every message posted in the bound text channel. |

## Requirements

- Python 3.11+
- FFmpeg + Opus runtime available for Discord voice playback
- Discord bot token with **Guilds**, **Voice States**, and **Message Content** intents enabled
- ElevenLabs account and API key (the free tier is enough for testing)

## Local setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r apps/bot/requirements.txt
   ```

3. Copy the example environment file and fill in real values:

   ```bash
   cp apps/bot/.env.example .env
   ```

   At a minimum set `DISCORD_TOKEN`, `ELEVENLABS_API_KEY`, and
   `ELEVENLABS_VOICE_ID`. The full list of variables (including optional
   voice tuning and limits) is documented inline in `.env.example`.

4. Run the bot:

   ```bash
   python -m apps.bot.main
   ```

## ElevenLabs setup

1. Sign in at <https://elevenlabs.io>.
2. From your profile menu, copy an API key into `ELEVENLABS_API_KEY`.
3. Open **Voices**, pick a voice you like, click the row, and copy the
   **Voice ID** into `ELEVENLABS_VOICE_ID`.
4. Optional: set `ELEVENLABS_MODEL_ID` (e.g. `eleven_turbo_v2_5` for low
   latency, `eleven_multilingual_v2` for higher quality) and the
   stability / similarity / style tuning knobs. Leave blank to use the
   provider defaults.

## Self-hosting with Docker

The repo ships an [`apps/bot/Dockerfile`](Dockerfile) that already installs
`ffmpeg` and runs the bot module. To deploy on any host that supports
Docker:

```bash
docker build -t ttstt-bot -f apps/bot/Dockerfile .
docker run --rm \
  -e DISCORD_TOKEN=... \
  -e ELEVENLABS_API_KEY=... \
  -e ELEVENLABS_VOICE_ID=... \
  ttstt-bot
```

Any platform that injects environment variables (Fly.io, Railway, Render,
a VPS via `systemd`, etc.) works the same way - the bot only reads from
`os.getenv`, never from baked-in config.

**Never commit your real `.env` file.** The repo's `.gitignore` already
excludes `.env`, `.env.local`, and `.env.*.local`; `apps/bot/.env.example`
is the only file checked in and is safe to read.

## Discord application configuration

In the [Discord Developer Portal](https://discord.com/developers/applications)
enable these gateway intents on your bot:

- Guilds
- Voice States
- Message Content (required for `/relay`)

Invite the bot using scopes `bot` and `applications.commands` and grant at
least these permissions in your target channels:

- Voice channel: **Connect**, **Speak**, **View Channel**, **Use Voice Activity**
- Text channel: **Send Messages**, **View Channel**, **Read Message History**

## Usage walk-through

1. Join a voice channel in your server.
2. In the text channel you want the bot bound to, run `/join`.
3. Run `/say message: hello world` to hear ElevenLabs read it back.
4. Run `/relay state: on` to have the bot read every subsequent message in
   that text channel. Run `/relay state: off` to stop. Bot messages and
   empty messages are ignored automatically.
5. Run `/leave` when you are done.
