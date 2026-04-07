# CSEN 174 — AI learning journal

**Project:** Mumble + Piper + Whisper (voice chat with TTS/STT)  
**How to use this file:** Each week, add a new dated section before the template at the bottom. Pull **real prompts** from Cursor chat history and note what actually happened (honest reflection, not marketing).

---

## Week of March 31, 2026

**Source chats:** Planning thread on repo layout (`apps/web`, `vendor/mumble`, CSEN 174 syllabus HTML), architecture pivots (local TTS → full-stack backend), plan doc updates.

### Three interesting prompts (and why each)

1. **Prompt (paraphrased):** *Design a voice chat service that uses Mumble for voice, Piper for TTS, with chat read aloud and voice transcribed to text; users pick Piper models and tune pitch/speed.*

   **Why it mattered:** It forced a concrete architecture choice early (where synthesis runs, how messages flow) instead of staying vague; the answer split into “bot injects audio” vs “each client plays TTS locally,” which changed everything downstream.

2. **Prompt (paraphrased):** *Does this idea match the CSEN 174 project requirements in the course HTML? What should change?*

   **Why it mattered:** It surfaced gaps between a cool integration and the **written** rubric (full-stack app, persistence, AI API + prompt construction, CI/tests). That turned a browser-heavy Piper idea into a **backend + Whisper + DB** plan we could defend to graders.

3. **Prompt (paraphrased):** *Drop ElevenLabs, use Whisper for STT, remove piper-tts-web from the plan; keep the AI learning journal using past chats.*

   **Why it mattered:** It simplified vendors (one STT story, server-only Piper) and linked course process (weekly journal) to **real** Cursor logs so reflection stays evidence-based instead of generic.

### One opportunity

AI-assisted planning mapped an unfamiliar stack (Mumble protocol, Piper ONNX, murmur) onto **course deliverables** quickly — especially tracing where `mumble-web` handles `message` events and voice, which would have taken longer reading cold.

### One challenge or risk

**Risk:** Treating “we use AI APIs” as enough for every syllabus bullet without checking the **exact** wording (e.g. programmatic prompt construction vs STT-only). Mitigation: small LLM JSON step or written TA/instructor confirmation, tracked in the project plan.

---

## Template — copy below for each new week

```markdown
## Week of [DATE]

**Source chats:** [Links or filenames, e.g. Cursor export / agent transcript id]

### Three interesting prompts (and why each)

1. **Prompt:**
   **Why it mattered:**

2. **Prompt:**
   **Why it mattered:**

3. **Prompt:**
   **Why it mattered:**

### One opportunity


### One challenge or risk


```

---

## Quick reference (from syllabus)

Each week’s submission should include:

- **3 prompts** you used in your work, each with **one sentence** on why (what worked, surprised you, or what you learned).
- **1 opportunity** — something AI helped you accomplish.
- **1 challenge or risk** — where AI fell short, was wrong, or created risk you managed.

Completion-graded; honesty over polish.
