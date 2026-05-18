# TTSTT — Peer Red Team Report (Received, Sprint 2 Lab)

One-paragraph summary: The TTSTT Discord bot joins voice channels, transcribes speech via Deepgram, and posts transcripts to text channels; listened text messages are synthesized and played in voice. The review focused on whether transcribed or TTS content is screened before it reaches other server members.

## Findings

### Category 2: Technical security

#### Finding 2.2 — Unmoderated Transcript Relay: Harmful Content Posted Verbatim

**Severity:** Major  
**Location (at review time):** `prototypes/noelle/bot/webhook_sender.py` (`send_as_member()`); `prototypes/noelle/bot/main.py` (`relay_segment()`)

**Vulnerability:** Speech-to-text transcripts were posted directly to Discord text channels with no content filtering. `AllowedMentions.none()` prevented `@everyone` / `@here` pings, but transcript text itself was unexamined. A user speaking slurs, phishing URLs, hate speech, or explicit content would have it transcribed and posted verbatim under their display name and avatar.

**Reproduction:** Join a voice channel where the bot is listening; speak an offensive phrase or `check out this site http://malicious-example.com`; observe the transcript posted with no moderation.

**Recommended fix:** Before posting, add a basic URL scanner to flag or suppress links; for production, integrate a lightweight moderation API (e.g., OpenAI Moderation API) for high-confidence harmful content.

---

### Category 3: Responsible AI

#### Finding 3.1 — Voice Disclosure of Sensitive Information Relayed Without Safeguard

**Severity:** Major  
**Background:** Role-played scenarios: (a) self-harm disclosure, (b) identifiable medical information, (c) minor disclosing age. In all cases the bot transcribed and posted verbatim to the text channel with no detection, flag, private alternative, crisis resource, or human-review path.

**Harm:** Public exposure of private disclosures; no support pathway (hotline, DM check-in).

**Recommended fix:** Add keyword- or ML-based detection between transcription and posting; route sensitive matches to a private DM to the speaker (or moderator hold); for self-harm, append crisis resources (e.g., 988); document in setup that voice is transcribed and posted. Apply similar screening to TTS paths so harmful text is not read aloud in voice.
