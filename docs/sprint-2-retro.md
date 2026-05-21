# Sprint 2 Retro

## What Went Well + Celebrate

- **Noelle** drove **Deepgram integration** for STT, however, we decided to not include this functionality after we found that it was difficult to rearrage discord's UDP packets for transcription.
- **Dana** built out the **TTS pipeline** and led **content moderation** work that made relayed speech and synthesized audio safer for real guilds.
- **Diego** completed the **architecture retrospective** and worked on the **documentation website**, giving the team a clearer record of vision and structure alongside the running bot.
- The team **merged peer red-team remediations** for the highest-impact AI safety findings ([PR #25](https://github.com/CSEN-SCU/csen-174-s26-team-project-ttstt/pull/25)), keeping Sprint 2 focused on the deployable `apps/bot` path rather than legacy prototypes.

## What Could Be Improved?

- **Kanban**: cards should clearly show **who owns each task**, **current status**, and **what “in progress” means** so the team is not blocked guessing who working on what.
- Carry **technical hardening** from the red team report onto the main bot on a predictable schedule (e.g. **TTS rate limiting** still in progress).

## Which Improvements Will the Team Commit to in Sprint 3?

- Adding **self-hosted Piper TTS** with the ability to change voices used for personalization (https://github.com/orgs/CSEN-SCU/projects/4?pane=issue&itemId=190647187&issue=CSEN-SCU%7Ccsen-174-s26-team-project-ttstt%7C31)
- **Use the Sprint 3 board as the source of truth**: every active task has an **assignee**, **status**, and **definition of done** updated at least once per lab; no “silent” work off-board.

## Red Team Response

In W7, SmartShop’s [red team report](red-team-report-ttstt-received.md) flagged supply-chain, CI, documentation, quota-abuse, and AI-safety issues across our **prototypes** and early `apps/bot` scaffold. We **acted on the two Major findings that map to AI API security and responsible AI**—**2.2** (unmoderated transcript relay) and **3.1** (sensitive voice disclosures posted publicly) by shipping **content moderation** on the consolidated bot: URL redaction, keyword-based sensitive routing (including a **988** note for self-harm), optional OpenAI Moderation API checks, TTS screening, and a **privacy notice on `/join`**, all merged in [**PR #25**](https://github.com/CSEN-SCU/csen-174-s26-team-project-ttstt/pull/25). We **did not re-open the historical prototype code paths** for findings aimed at `prototypes/noelle`, `prototypes/diego`, etc.—those trees were experiments we are not extending; instead we **ported the intent** to `apps/bot` (e.g. **`apps/bot/.env.example`** for required secrets, and **TTS rate limiting** as follow-up on the main listener queue). **2.1** (no LLM prompt-injection surface) we treat as an **architectural strength**; no change required unless we add an LLM feature later.

## Sprint 3 Commitments

- Add a way to change the voice preferences for the user for Deepgram (https://github.com/orgs/CSEN-SCU/projects/4/views/1?pane=issue&itemId=190647132&issue=CSEN-SCU%7Ccsen-174-s26-team-project-ttstt%7C30)
- Complete the integration for the self-hosted Piper TTS for lower latency and with the ability to change voicse (https://github.com/orgs/CSEN-SCU/projects/4?pane=issue&itemId=190647187&issue=CSEN-SCU%7Ccsen-174-s26-team-project-ttstt%7C31)
