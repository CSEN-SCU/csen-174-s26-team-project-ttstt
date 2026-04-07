# Product vision — TTSTT

## 1a. Product vision statement (Moore template + POWERED BY)

**FOR** Discord communities—study servers, hobby groups, accessibility-minded guilds, and teams that already **live in text and voice channels**—**WHO** need **accessible participation**: people who are **hard of hearing or Deaf** and depend on **text for what was said**; people who are **non-verbal** or **prefer typing** and need their words **heard in voice**, not only read in a fast-moving channel; and anyone in **noisy environments** or on **low-quality gear** where **clean listening isn’t reliable**—and who today rely on **manual repeats**, **screenshots**, or **fragmented workarounds** across bots and DMs,

**THE** **TTSTT** (Text To Speech To Text)

**IS A** **Discord bot plus companion API** that sits in your **server’s voice and text channels**

**THAT** turns **spoken contributions** into **postable text** and **reads written chat aloud** in **voice** with **each user’s chosen synthetic voice** (model, pacing, expressiveness, pitch, and speed)—so members who lean on **ears**, **eyes**, or **both** share the **same room** without bolting on a separate captioning product,

**UNLIKE** using **Discord alone**—where voice doesn’t become durable text by default and long text doesn’t **speak to the VC**—or **unlike** expecting everyone to **migrate** to a single VC stack just to get **basic bridging**,

**OUR PRODUCT** **meets people on Discord**, uses **slash and chat commands** as the primary interface, and runs **speech AI on infrastructure you control** (API + Postgres) so prefs and processing stay **transparent and tunable** for the community,

**POWERED BY** **large-model automatic speech recognition** that converts spoken utterances into accurate, postable text **together with** **neural text-to-speech** that renders lines as natural, consistent audio—fast enough to feel usable during **live voice hangs**.

---

## 1b. Vision narrative

**Problem in context.** Discord blends **high-rate text** and **push-to-talk voice**, but the two modalities stay **loosely coupled**: voice doesn’t automatically become a **searchable thread** for **hard-of-hearing or Deaf** users; **non-verbal** or **text-first** participants watch the **VC audio lane** pass them by unless someone reads their messages aloud; and **noisy rooms** or bad mics make **listening a gamble**. The platform isn’t built to **close that loop** out of the box—so access becomes **private negotiation** (please repeat, please look at chat) instead of a **shared norm**.

**How AI makes this possible.** **Automatic speech recognition** at current quality can turn **short captures** into **messages in-channel** without a human captioner. **Neural text-to-speech** (e.g. **Piper-class** voices) can **read chat into the voice channel** with **per-user** tuning so identity and prosody stay recognizable. Server-side **normalization and pitch/tempo** keep clips **listenable** across headsets. That bundle is what makes **“speech becomes text”** and **“text becomes voice”** **routine** inside an existing Discord workflow.

**Without-AI test.** Strip **ASR** and you revert to **typing or guessing**—the “what was said” promise for people who **don’t hear VC** collapses. Strip **neural TTS** and typed lines **don’t reliably reach listeners in voice**—you lose **room-scale readout** with **personal voices**. A plain Discord bot without those capabilities is **incrementally helpful**; it does **not** deliver the **accessibility core** of TTSTT. **AI is load-bearing**, not decorative.
