# Sprint 2 — Peer Red Team Remediations

**Peer report:** [red-team-report-ttstt-received.md](red-team-report-ttstt-received.md) — SmartShop (Divya Bengali, Shreeya Koritala, Caroline Tapia, Terry Chen), May 12, 2026, against TTSTT.

This sprint we remediated **two** findings from that report: one **AI API security** issue and one **responsible AI** issue (see summary table in the peer report). Implementation is on the consolidated bot in `apps/bot/`, not the historical `prototypes/` paths cited in the review.

---

## 1. Unmoderated transcript relay (AI API security)

| | |
|---|---|
| **Source finding** | [Finding 2.2 — Unmoderated Transcript Relay: Harmful Content Posted Verbatim](red-team-report-ttstt-received.md#L82-L99) (Category 2: AI API Security) |
| **Merged PR** | _Replace with merged PR URL after landing (single PR for both fixes)_ |

The peer review found raw Deepgram transcripts posted to Discord with no screening for slurs, phishing URLs, or other harmful text (`AllowedMentions.none()` only blocked pings). We added `apps/bot/content_moderation.py` and run every STT transcript through `moderate_for_transcript()` in `apps/bot/stt.py` before `channel.send()`. URLs are replaced with `[link removed]`, and optional `OPENAI_API_KEY` enables OpenAI Moderation API checks for hate, harassment, and violence—matching the report’s recommended URL scan and lightweight moderation API.

---

## 2. Sensitive voice disclosures relayed publicly (responsible AI)

| | |
|---|---|
| **Source finding** | [Finding 3.1 — Voice Disclosure of Sensitive Information Relayed Without Safeguard](red-team-report-ttstt-received.md#L103-L114) (Category 3: Responsible AI) |
| **Merged PR** | _Replace with merged PR URL after landing (single PR for both fixes)_ |

The report’s role-play scenarios (self-harm, medical information, minor age disclosure) were posted verbatim to the text channel with no private alternative or crisis resources; the same concern applied to unscreened TTS (`/say` in Diego’s prototype). We route keyword-matched sensitive transcripts to a **private DM** to the speaker (988 crisis line for self-harm), document transcription in the `/join` response and `apps/bot/README.md`, and run listened-user TTS through `moderate_for_tts()` in `apps/bot/main.py` so sensitive text and links are not read aloud in voice.
