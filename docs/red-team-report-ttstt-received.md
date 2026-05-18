
Red Team Report: TTSTT
Attacking team: SmartShop (Divya Bengali, Shreeya Koritala, Caroline Tapia, Terry Chen) Target team: TTSTT (Noelle Evanich, Diego Silva, Dana Steinke) Repo: https://github.com/CSEN-SCU/csen-174-s26-team-project-ttstt Date: May 12, 2026

Product Summary
TTSTT (Text To Speech To Text) is a Discord bot that bridges voice and text in Discord servers. It has three prototype implementations committed to the repo: Noelle's bot captures live voice from a Discord voice channel, sends audio to Deepgram's speech-to-text API, and posts the resulting transcript to a text channel via a webhook impersonating each speaker's display name and avatar. Diego's bot accepts a /say slash command, synthesizes the text via Azure Cognitive Services neural TTS, and plays audio back into the voice channel. Dana's prototype is a local CLI tool that records from a microphone and transcribes using a local faster-whisper model (no API key required). A shared apps/bot/ scaffolds the join/leave/status commands. There is no public web deployment as the application surface is in a Discord server plus the public GitHub repository.
We probed: the public GitHub repo on all branches, all source files on main, the CI/CD workflow, git commit history across all visible commits, and the documentation.

Threat Model
External attacker (repo reader): The repo is public and contains all application code, dependency declarations, CI configuration, and secrets-management documentation. A reader can identify which external APIs are in use (Deepgram, Azure Speech, ElevenLabs), understand the authentication flow, and look for improperly committed credentials without running anything. This is the most plausible non-Discord threat because there is no web attack surface.
Insider (Discord server member): Any member of a Discord server the bot has been added to can issue slash commands (/join, /leave, /say, /status). Since Discord slash commands require no additional auth beyond server membership, a malicious or careless server member is the primary runtime abuse vector — they can queue TTS requests, trigger transcription in channels they have access to, or speak harmful content through the ASR pipeline.

Findings
Category 1: Technical Security

Finding 1.1 — Unversioned GitHub URL Dependency (Supply Chain)
Severity: Major
Location: apps/bot/requirements.txt line 2, prototypes/noelle/requirements.txt line 2
Vulnerability: Both requirements files pin the voice-receive extension as:
discord-ext-voice-recv @ git+https://github.com/imayhaveborkedit/discord-ext-voice-recv.git

This installs directly from the HEAD commit of a third-party repository with no version tag and no pinned commit hash.
Reproduction steps:
Open apps/bot/requirements.txt in the public repo.
Observe discord-ext-voice-recv @ git+https://github.com/imayhaveborkedit/discord-ext-voice-recv.git — no @<tag> or @<commit-sha> suffix.
Note that any pip install -r requirements.txt will resolve to whatever HEAD is at that moment.
If the upstream repo is compromised, force-pushed, or taken over, the next fresh install silently executes arbitrary Python code inside the bot's runtime — which has access to all environment variables including DISCORD_TOKEN, DEEPGRAM_API_KEY, etc.
Recommended fix: Pin to a specific release tag or commit SHA, e.g.:
discord-ext-voice-recv @ git+https://github.com/imayhaveborkedit/discord-ext-voice-recv.git@v0.5.0

Or fork the dependency into the team's own GitHub org and pin to a specific commit of the fork. Periodically review upstream changes before bumping the pin.

Finding 1.2 — CI Secret Exposed to All Job Steps
Severity: Minor
Location: .github/workflows/ci.yml lines 12–17
Vulnerability: The ELEVENLABS_API_KEY secret is declared at the job: level under env:, making it available as an environment variable to every step in the job including actions/checkout@v5 and actions/setup-python@v6 not just the step that runs tests.
jobs:
  test:
    env:
      ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
    steps:
      - uses: actions/checkout@v5         # has access to the key
      - uses: actions/setup-python@v6     # has access to the key
      - run: pip install pytest            # has access to the key
      - run: python -m pytest unittests   # only this step needs it

If a malicious third-party action in the job reads environment variables (e.g., a compromised actions/checkout), it has access to the key.
Reproduction steps:
Open .github/workflows/ci.yml.
Observe env: is at the jobs.test: level, not at the individual run: step level.
Recommended fix: Move the secret injection to only the pytest step:
- name: Run test suite
  run: python -m pytest unittests
  env:
    ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}


Finding 1.3 — Missing .env.example for Main Bot and Noelle's Prototype
Severity: Minor
Location: apps/bot/ (no .env.example), prototypes/noelle/ (no .env.example)
Vulnerability: Only Diego's prototype (prototypes/diego/.env.example) documents what environment variables are required. The main deployable bot (apps/bot/main.py) expects DISCORD_TOKEN and Noelle's bot (prototypes/noelle/bot/main.py) expects both DISCORD_TOKEN and DEEPGRAM_API_KEY, but neither directory has a documented contract. A new developer setting up either bot has no documented guide to required secrets, increasing the risk of guessing wrong variable names or hardcoding values as a workaround.
Recommended fix: Add .env.example files to apps/bot/ and prototypes/noelle/ mirroring the pattern in prototypes/diego/.env.example, listing every expected variable with a placeholder value and a comment.

Finding 1.4 — No Per-User Rate Limit on /say (TTS Quota Abuse)
Severity: Minor
Location: prototypes/diego/discord_bot/bot.py, _register_commands() → say command
Vulnerability: The /say command enforces a 2,000-character message cap but has no per-user cooldown, no daily quota cap, and no per-server audio queue depth limit. The _audio_queue is unbounded (asyncio.Queue() with no maxsize). A user with server access could rapidly queue hundreds of /say requests, accumulating Azure TTS API calls (each billed per character) and filling the in-memory audio queue. Discord's native slash command rate limiting provides some protection but does not cap API cost.
Reproduction steps:
Join a Discord server where the bot is running.
Use a script or rapid manual input to send /say hello many times in quick succession.
Observe the audio queue growing and Azure API calls accumulating without server-side throttling.
Recommended fix: Add a per-user cooldown (e.g., one /say every 5 seconds) using discord.app_commands.checks.cooldown(), and cap queue depth with asyncio.Queue(maxsize=20) to shed excess requests.

Category 2: AI API Security

Finding 2.1 — No Prompt Injection Surface (Null Result — Architectural Strength)
Severity: N/A
We specifically looked for prompt injection paths: places where user-controlled input flows unsanitized into an LLM instruction context.
What we tried: Reviewed the full data flow across all three prototype implementations. Deepgram receives raw WAV audio bytes and returns a transcript — no prompt, no instruction context, no system message. Azure Speech receives raw text and returns audio — no LLM involved. Dana's implementation uses a local faster-whisper model with no external LLM call at all.
Null result: Because TTSTT uses specialized ASR and TTS APIs rather than a general-purpose instruction-following LLM, there is no system prompt to inject into. This is a meaningful security advantage. If the team later adds an LLM feature (e.g., a "summarize the conversation" command), this advantage disappears and prompt injection should be re-evaluated at that point.

Finding 2.2 — Unmoderated Transcript Relay: Harmful Content Posted Verbatim
Severity: Major
Location: prototypes/noelle/bot/webhook_sender.py, send_as_member() method; prototypes/noelle/bot/main.py, relay_segment()
Vulnerability: Speech-to-text transcripts are posted directly to Discord text channels with no content filtering of any kind:
await webhook.send(
    content=content,           # raw Deepgram output, no moderation
    username=member.display_name,
    avatar_url=member.display_avatar.url,
    allowed_mentions=discord.AllowedMentions.none(),
)

AllowedMentions.none() prevents @everyone/@here pings, but the transcript text itself is unexamined. A user speaking any content: slurs, links to phishing URLs, hate speech, explicit content, will have it transcribed and posted verbatim into the text channel under their display name and avatar.
Reproduction steps:
Add the bot to a Discord server with Noelle's prototype running.
Join a voice channel where the bot is listening.
Speak the phrase "check out this site http://malicious-example.com" or any offensive phrase.
Observe the transcript posted to the linked text channel with no moderation.
Recommended fix: Before posting, run transcript text through Discord's AllowedMentions policy (already done), and add a basic URL scanner (re.search(r'https?://', content)) to flag or suppress links. For production, integrate a lightweight moderation API call (e.g., OpenAI's Moderation API, free tier) to flag high-confidence hate speech or harmful content before posting.

Category 3: Responsible AI

Finding 3.1 — Voice Disclosure of Sensitive Information Relayed Without Safeguard
Severity: Major
Background: We role-played three scenarios a vulnerable user might encounter with the running Noelle bot: (a) a person disclosing self-harm thoughts ("I've been thinking about hurting myself lately"), (b) a person sharing identifiable medical information ("I have bipolar disorder and stopped my medication"), and (c) a minor disclosing age ("I'm 14 and my parents don't know I'm in this server"). We analyzed the code path for each.
What the app currently does: In all three scenarios, the bot captures the audio, sends it to Deepgram's API, receives the transcript, and posts it verbatim to the Discord text channel under the speaker's display name and avatar — publicly visible to all members of that server with access to the channel. There is no content detection, no flag, no private alternative, no crisis resource, and no logging for human review. The bot's behavior is architecturally identical regardless of what is said.
For users in a vulnerable moment, this causes real harm in two ways:
Public exposure: A private disclosure ("I've been thinking about hurting myself") becomes a server-visible text message posted under the person's name. Other members see it without context; the person loses control of the disclosure immediately.
No support pathway: There is no acknowledgement, no "are you okay?", no hotline mention, no DM to the user. The content just appears in the channel and the bot continues normally.
Consider the following mitigations:
Add a keyword-based or ML-based detection step between transcribe_wav() and send_as_member(). If the transcript matches a sensitive pattern (self-harm, medical PII, age disclosure of a minor), route it to a private DM to the speaker instead of the public channel, or hold it for a human moderator.
For self-harm content specifically, append a brief crisis resource: "If you or someone you know is struggling, the 988 Suicide & Crisis Lifeline is available by call or text."
Document in the bot's server-facing setup guide that all voice content is transcribed and posted, so members can make an informed decision before speaking.
The same logic applies to the /say TTS command in Diego's prototype: the command allows a user to make the bot speak any text aloud in the voice channel, including crisis disclosures or harmful content directed at other members. A character limit is enforced but content is not screened.

Summary Table
#
Category
Finding
Severity
1.1
Technical
Unversioned GitHub dependency (supply chain)
Major
1.2
Technical
CI secret exposed to all job steps
Minor
1.3
Technical
Missing .env.example for main bot and Noelle prototype
Minor
1.4
Technical
No rate limit on /say — TTS quota abuse
Minor
2.1
AI API
No prompt injection surface (null result, architectural strength)
N/A
2.2
AI API
Unmoderated transcript relay — harmful content posted verbatim
Major
3.1
Responsible AI
Sensitive disclosures relayed publicly without safeguard
Major

Top finding for lab presentation: Finding 1.1 (supply chain via unversioned git dependency) + Finding 3.1 (sensitive voice disclosure relayed publicly). Together they represent the most impactful combination of technical risk and user harm potential.
