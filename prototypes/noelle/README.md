# Discord Voice-to-Text Relay (Deepgram)

This bot joins a live Discord voice channel, transcribes spoken audio with Deepgram, and posts transcript text into the same text channel where `/join` was run. Transcript messages are sent by webhook using each speaker's display name and avatar.

## Features

- `/join`: Connect to your current voice channel and start relaying transcripts.
- `/leave`: Stop relaying and disconnect from voice.
- `/status`: Show current voice + text relay targets.
- Per-speaker buffering with silence-based chunking to avoid message spam.
- Transcript delivery via channel webhooks for speaker name/avatar fidelity.

## Requirements

- Python 3.11+ recommended
- FFmpeg + Opus environment required by Discord voice stack
- Discord bot token
- Deepgram API key
- If you hit repeated `discord.opus.OpusError: corrupted stream`, use Python 3.11 specifically (3.14 has been less stable with current receive stack).

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   This project intentionally installs `discord-ext-voice-recv` from the upstream GitHub repository to pick up decoder/router fixes not always present in the latest PyPI release.

3. Copy and edit environment values:

   ```bash
   cp .env.example .env
   ```

   Set:
   - `DISCORD_TOKEN`
   - `DEEPGRAM_API_KEY`

4. Run the bot:

   ```bash
   python -m bot.main
   ```

## Discord Bot Configuration

Enable these gateway intents for the bot:

- `Guilds`
- `Voice States`

Required permissions:

- In target voice channel: `Connect`, `Speak`, `View Channel`
- In target text channel: `Send Messages`, `Manage Webhooks`, `View Channel`

## Usage

1. Join the voice channel you want to monitor.
2. In a text channel, run `/join`.
3. Speak in voice; transcript messages should appear in that same text channel.
4. Run `/status` to verify the active relay.
5. Run `/leave` to stop.

## Notes

- "Same channel" is defined as the text channel where `/join` was invoked.
- If `Manage Webhooks` is missing, the bot falls back to normal bot messages with `**DisplayName:** transcript`.
- Audio is chunked and transcribed after short silence windows, so output is near-real-time rather than word-by-word.
- If Discord sends malformed or lossy voice packets, the listener now auto-restarts instead of staying down after a decode failure.
- A restart circuit breaker halts receive after repeated decoder failures to prevent infinite restart thrashing.
