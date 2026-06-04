# Demo video script (TTSTT-as-narrator)

Recording playbook for **CSEN 174 W10 Part 2**: a screen recording (≤ 2 minutes) where **narration is pasted into the control text channel** and **spoken by TTSTT** in voice. The screen shows only Discord—no IDE, terminal, architecture slides, or dev tools.

Same happy path as the live demo and [`docs/help/index.html`](help/index.html): `/join` → `/tts_listen_user` → typed messages → **`/tts_provider_set`** (Deepgram ↔ Piper) → voice prefs → `/help` → `/leave`.

---

## Prerequisites

Before recording:

1. **Bot online** on the demo guild (deployed host running `python -m apps.bot.main`).
2. **Recorder account** can use slash commands in the demo server.
3. **Voice channel** chosen (e.g. `#demo-voice`); recorder **joined to VC** before starting.
4. **Control text channel** chosen (e.g. `#demo-control`); keep it visible in the recording.
5. **`HELP_URL`** works (`/help` opens the Netlify guide).
6. **FFmpeg** available on the bot host (voice playback).
7. **Both TTS backends configured** on the bot host if you will show provider switching: `DEEPGRAM_API_KEY` and Piper (`PIPER_MODEL_DIR` + `piper` binary). Verify `/tts_provider_set` offers both choices before recording.
8. **Dry-run one paste line**: `/join`, `/tts_listen_user` (your account), send *"Test line for demo video."* — confirm speech in VC and OBS captures it.

**Moderation-safe paste rules** (see [`apps/bot/content_moderation.py`](../apps/bot/content_moderation.py)):

- No URLs (`http://`, `https://`, domains) in paste lines — links are blocked from TTS.
- Avoid mental-health, self-harm, and minor-age phrasing in narration.
- Keep each paste block **under ~300 characters**.

---

## OBS / audio checklist

| Setting | Why |
|--------|-----|
| Capture **Discord window** (or full screen with Discord focused) | Part 2 must be user-facing UI |
| Enable **application / desktop audio** (not mic-only) | TTSTT plays in the **voice channel**; graders must **hear** neural TTS on the MP4 |
| Disable or lower mic if it drowns out bot audio | Optional: mic off for this take |
| 1080p or 720p, 30 fps | Readable slash-command UI |
| **Wait** until each line **finishes speaking** before the next paste or slash command | Avoid overlapping queue / clipped narration |

**Latency:** After each message, wait for the bot to finish playback in VC (typically ~3–12 s per line depending on length and provider).

---

## Recording flow (overview)

```text
Join VC → Start OBS → Record
  → Paste lines 1–2 (problem + product)
  → /join → Paste line 3
  → /tts_listen_user (self) → Paste line 4
  → Paste line 5 (demo user message) — key moment
  → Paste line 6
  → /tts_provider_set → Piper (local) → Paste line 7
  → Paste line 8 (same message, Piper voice)
  → /tts_voice_set (visible change) → Paste line 9
  → Paste line 10 (second demo message)
  → /help → Paste line 11
  → /leave → Paste line 12
→ Stop OBS → Trim to ≤ 2:00 → Export MP4
```

**Pre-roll:** You may run `/join` and `/tts_listen_user` before pressing record, but the **final cut should show both commands on screen** so the happy path matches the live demo.

---

## Shot list

| Step | Time target | On screen | Paste this message (after prior step completes) | Wait for | Notes |
|------|-------------|-----------|--------------------------------------------------|----------|-------|
| 1 | 0:00–0:10 | Demo server; user in VC; control channel visible | See [Line 1](#line-1) | TTS ends in VC | Opens with the problem |
| 2 | 0:10–0:20 | Same | See [Line 2](#line-2) | TTS ends | What TTSTT is |
| 3 | 0:20–0:30 | Run `/join`; dismiss privacy notice if shown | — | Bot connected to VC | Slash command must be visible |
| 4 | 0:30–0:40 | After join completes | See [Line 3](#line-3) | TTS ends | Explains join |
| 5 | 0:40–0:48 | Run `/tts_listen_user` → select **your** demo account | — | Ephemeral confirmation | Must match account that pastes lines |
| 6 | 0:48–0:56 | After listen is active | See [Line 4](#line-4) | TTS ends | Explains listen |
| 7 | 0:56–1:08 | Same (default provider: Deepgram) | See [Line 5](#line-5) | TTS ends | **Demo user message** — not meta-narration |
| 8 | 1:08–1:18 | Brief pause; VC activity visible | See [Line 6](#line-6) | TTS ends | Confirms text → voice (cloud) |
| 9 | 1:18–1:28 | Run `/tts_provider_set` → **Piper (local)** | — | Ephemeral confirmation | Provider switch on screen |
| 10 | 1:28–1:38 | After provider update | See [Line 7](#line-7) | TTS ends | Explains cloud vs local |
| 11 | 1:38–1:48 | Same | See [Line 8](#line-8) | TTS ends | Hear Piper voice |
| 12 | 1:48–1:55 | Run `/tts_voice_set` (e.g. `speed:1.2` or different `voice:`) | — | Command confirmation | One clear change on screen |
| 13 | 1:55–2:02 | After voice set succeeds | See [Line 9](#line-9) | TTS ends | Voice prefs |
| 14 | 2:02–2:08 | Same | See [Line 10](#line-10) | TTS ends | Hear changed settings |
| 15 | 2:08–2:14 | Run `/help` (link appears in Discord — do not paste URL in chat) | — | Help embed/link | URL only via slash command |
| 16 | 2:14–2:20 | After help posts | See [Line 11](#line-11) | TTS ends | How visitors try it |
| 17 | 2:20–2:24 | Run `/leave` | — | Bot disconnects | |
| 18 | 2:24–2:30 | After leave | See [Line 12](#line-12) | TTS ends | Closing line |

**Target runtime:** ~2:00–2:30 raw; **trim to ≤ 2:00** in edit. If over budget, cut in this order: (1) Line 9 narration — keep `/tts_voice_set` + Line 10 only; (2) Line 11 — go straight to `/leave` after Line 10; (3) tighten pauses between paste lines.

**Optional on-screen captions** (add in editor) for silent beats: e.g. “`/join` — bot joins your voice channel” during step 3 if VC audio is quiet in the recording.

---

## Copy-paste appendix

Paste **one block per message**. Send only the quoted sentence (no quotes).

<a id="line-1"></a>

### Line 1

```text
On Discord, fast text and live voice run side by side. Typed messages usually do not reach people who are only listening in voice.
```

<a id="line-2"></a>

### Line 2

```text
TTSTT is a Discord bot that reads selected text aloud in the voice channel, using a synthetic voice you can customize per person.
```

<a id="line-3"></a>

### Line 3

```text
I used the join command. The bot connected to this voice channel, and this text channel is now the control channel.
```

<a id="line-4"></a>

### Line 4

```text
Listen user tells the bot to read my messages from this channel aloud in voice.
```


### Line 7 (after `/tts_provider_set` → Piper)

```text
Provider set lets me pick the engine. Deepgram Aura runs in the cloud. Piper runs locally on the server for lower latency.
```

<a id="line-8"></a>
v
### Line 8 (demo message on Piper)

```text
Same study session check-in, now spoken with a local Piper voice.
```

<a id="line-9"></a>

### Line 9

```text
Each person can set voice, speed, and pitch for this server with the voice set command.
```

<a id="line-10"></a>

### Line 10 (second demo message)

```text
Same me in chat, different voice settings in voice.
```

<a id="line-11"></a>

### Line 11

```text
At demo night, join our server or add the bot to yours. Slash help opens the full command guide.
```

<a id="line-12"></a>

### Line 12

```text
Leave disconnects the bot. TTSTT brings typed chat into voice so text-first members are heard in the room.
```

---

## Dry-run checklist (timing)

Run once without OBS to log real timings on your demo guild. Adjust pauses or trim lines if total exceeds **2:00**.

| Step | Planned | Actual (fill in) |
|------|---------|------------------|
| Lines 1–2 | ~20 s | |
| `/join` + Line 3 | ~20 s | |
| `/tts_listen_user` + Line 4 | ~16 s | |
| Lines 5–6 (Deepgram) | ~22 s | |
| `/tts_provider_set` + Lines 7–8 (Piper) | ~30 s | |
| `/tts_voice_set` + Lines 9–10 | ~26 s | |
| `/help` + Line 11 | ~16 s | |
| `/leave` + Line 12 | ~14 s | |
| **Total (raw)** | **~2:30** | |
| **After trim** | **≤ 2:00** | |

- [ ] VC audio audible on a test recording (5 s clip)
- [ ] No paste line blocked (no URLs in chat)
- [ ] Stranger can follow without narration text on screen (audio-only test)

---

## Post-production and submission

1. **Trim** to ≤ 2:00; cut dead air at start/end.
2. **Export** `ttstt-demo-w10.mp4` (or team naming convention).
3. **Upload** unlisted YouTube (or equivalent); submit URL to Camino.
4. **Demo laptop:** copy MP4 locally; queue in media player — must play in **under 10 seconds** **offline** (no network for fallback).
5. **README:** add the public video link in [Demo video](../README.md#demo-video) (portfolio front door).

**Do not include** in the video: codebase, architecture diagrams, terminal, Developer Portal, or prompt engineering.

---

## Optional: rehearsed failure clip (Part 1 fallback)

Separate **~10 s** take (not in the 2-minute video):

1. Bot joined and listening.
2. Paste: `Check out https://example.com for notes.`
3. Show bot **does not** read the message aloud (link blocked); explain verbally at the station if asked.

Use this at the demo table when an in-flow safety block happens — not as Part 2 main content.

---

## Quick links (for operators, not for paste)

| Resource | URL |
|----------|-----|
| Add bot | `https://discord.com/oauth2/authorize?client_id=1496265708215075016` |
| Help guide | `https://kaleidoscopic-crostata-402ea4.netlify.app/` |
| GitHub | `https://github.com/CSEN-SCU/csen-174-s26-team-project-ttstt` |

Use `/help` on screen for the help URL — never paste these into chat during recording.
