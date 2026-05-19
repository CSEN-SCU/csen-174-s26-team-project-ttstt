# Sprint 2 Retro

## What Went Well + Celebrate

- **Noelle** drove **Deepgram integration** for the consolidated bot—wiring ASR (and related API usage) so voice can flow toward in-channel transcription.
- **Dana** built out the **TTS pipeline** and led **content moderation** work that made relayed speech and synthesized audio safer for real guilds.
- **Diego** completed the **architecture retrospective** and the **documentation website**, giving the team a clearer record of vision and structure alongside the running bot.
- The team **merged peer red-team remediations** for the highest-impact AI safety findings ([PR #25](https://github.com/CSEN-SCU/csen-174-s26-team-project-ttstt/pull/25)), keeping Sprint 2 focused on the deployable `apps/bot` path rather than legacy prototypes.

## What Could Be Improved?

- **Speech-to-text reliability** still needs work—especially **how Discord voice UDP packets are captured, ordered, and prepared** before they reach Deepgram—so transcripts match what users actually said in voice chat.
- **Kanban**: cards should clearly show **who owns each task**, **current status**, and **what “in progress” means** so the team is not blocked guessing who is on STT vs TTS vs docs.
- Carry **technical hardening** from the red team report onto the main bot on a predictable schedule (e.g. **TTS rate limiting** still in progress).

## Which Improvements Will the Team Commit to in Sprint 3?

- **Finish STT end-to-end**: a member can **speak in voice chat** and see **accurate transcription in the linked text channel**—including stable handling of Discord’s voice packet stream ([issue #27](https://github.com/CSEN-SCU/csen-174-s26-team-project-ttstt/issues/27)).
- **Use the Sprint 3 board as the source of truth**: every active task has an **assignee**, **status**, and **definition of done** updated at least once per lab; no “silent” work off-board.

## Red Team Response

In W7, SmartShop’s [red team report](red-team-report-ttstt-received.md) flagged supply-chain, CI, documentation, quota-abuse, and AI-safety issues across our **prototypes** and early `apps/bot` scaffold. We **acted on the two Major findings that map to AI API security and responsible AI**—**2.2** (unmoderated transcript relay) and **3.1** (sensitive voice disclosures posted publicly)—by shipping **content moderation** on the consolidated bot: URL redaction, keyword-based sensitive routing (including a **988** note for self-harm), optional OpenAI Moderation API checks, TTS screening, and a **privacy notice on `/join`**, all merged in [**PR #25**](https://github.com/CSEN-SCU/csen-174-s26-team-project-ttstt/pull/25). We **did not re-open the historical prototype code paths** for findings aimed at `prototypes/noelle`, `prototypes/diego`, etc.—those trees were experiments we are not extending; instead we **ported the intent** to `apps/bot` (e.g. **`apps/bot/.env.example`** for required secrets, and **TTS rate limiting** as follow-up on the main listener queue). **2.1** (no LLM prompt-injection surface) we treat as an **architectural strength**; no change required unless we add an LLM feature later.

## Sprint 3 Commitments

- **STT: voice → accurate chat transcript** — [Issue #27: figure out how to rearrange discord's udp packets for transcription](https://github.com/CSEN-SCU/csen-174-s26-team-project-ttstt/issues/27). **Done** when a user can **speak in the voice channel** and the bot **posts a correct transcript** to the configured text channel during a live hang.
