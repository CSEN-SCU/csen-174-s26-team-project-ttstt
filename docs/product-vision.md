# Product vision — TTSTT

## 1a. Product vision statement (Moore template + POWERED BY)

**FOR** Discord communities—study servers, hobby groups, accessibility-minded guilds, and teams that already **live in text and voice channels**—**WHO** need **accessible participation**: people who are **non-verbal** or **prefer typing** and need their words **heard in voice**, not only read in a fast-moving channel; and anyone who wants **written chat to reach voice-channel participants** without someone manually reading aloud—and who today rely on **manual readouts**, **@mentions in VC**, or **fragmented workarounds** across bots and DMs,

**THE** **TTSTT** (Text To Speech To Text)

**IS A** **Discord bot plus companion API** that sits in your **server’s voice and text channels**

**THAT** **reads written chat aloud** in **voice** with **each user’s chosen synthetic voice** (model, pacing, expressiveness, pitch, and speed)—so members who lean on **ears**, **eyes**, or **both** share the **same room** without bolting on a separate reader bot,

**UNLIKE** using **Discord alone**—where long text doesn’t **speak to the VC** by default—or **unlike** expecting everyone to **migrate** to a single VC stack just to get **basic text-to-voice bridging**,

**OUR PRODUCT** **meets people on Discord**, uses **slash and chat commands** as the primary interface, and runs **speech AI on infrastructure you control** (API + Postgres) so prefs and processing stay **transparent and tunable** for the community,

**POWERED BY** **neural text-to-speech** that renders lines as natural, consistent audio—fast enough to feel usable during **live voice hangs**.

---

## 1b. Vision narrative

**Problem in context.** Discord blends **high-rate text** and **push-to-talk voice**, but the two modalities stay **loosely coupled**: **non-verbal** or **text-first** participants watch the **VC audio lane** pass them by unless someone reads their messages aloud; and busy voice hangs mean **typed contributions are easy to miss** for people who are **in the channel but listening, not scrolling**. The platform isn’t built to **carry chat into voice** out of the box—so participation becomes **private negotiation** (please read that, please look at chat) instead of a **shared norm**.

**How AI makes this possible.** **Neural text-to-speech** (e.g. **Deepgram Aura** or **Piper-class** voices) can **read selected chat into the voice channel** with **per-user** tuning so identity and prosody stay recognizable. Server-side **playback and queueing** keep lines **listenable** across headsets during live hangs. That bundle is what makes **“text becomes voice”** **routine** inside an existing Discord workflow.

**Without-AI test.** Strip **neural TTS** and typed lines **don’t reliably reach listeners in voice**—you lose **room-scale readout** with **personal voices**. A plain Discord bot without synthesis is **incrementally helpful**; it does **not** deliver the **accessibility core** of TTSTT. **TTS is load-bearing**, not decorative.

**Scope note.** The deployable bot in `apps/bot` is **TTS-only** today. **Speech-to-text** (captions for Deaf/hard-of-hearing users, voice → durable text) is **not** in the current product scope; it may return if the team reopens bidirectional bridging.

---

## How Might We...

**How might we** bring written chat into the voice channel **as we aim to** ensure text-first and non-verbal members are **heard in the room**—with natural, per-user voices—during live Discord hangs?
