# Architecture retrospective — TTSTT

## Product vision statement (current)
**FOR** Discord communities—study servers, hobby groups, accessibility-minded guilds, and teams that already **live in text and voice channels**—**WHO** need **accessible participation**: people who are **hard of hearing or Deaf** and depend on **text for what was said**; people who are **non-verbal** or **prefer typing** and need their words **heard in voice**, not only read in a fast-moving channel; and anyone in **noisy environments** or on **low-quality gear** where **clean listening isn’t reliable**—and who today rely on **manual repeats**, **screenshots**, or **fragmented workarounds** across bots and DMs,
**THE** **TTSTT** (Text To Speech To Text)
**IS A** **Discord bot plus companion API** that sits in your **server’s voice and text channels**
**THAT** turns **spoken contributions** into **postable text** and **reads written chat aloud** in **voice** with **each user’s chosen synthetic voice** (model, pacing, expressiveness, pitch, and speed)—so members who lean on **ears**, **eyes**, or **both** share the **same room** without bolting on a separate captioning product,
**UNLIKE** using **Discord alone**—where voice doesn’t become durable text by default and long text doesn’t **speak to the VC**—or **unlike** expecting everyone to **migrate** to a single VC stack just to get **basic bridging**,
**OUR PRODUCT** **meets people on Discord**, uses **slash and chat commands** as the primary interface, and runs **speech AI on infrastructure you control** (API + Postgres) so prefs and processing stay **transparent and tunable** for the community,
**POWERED BY** **large-model automatic speech recognition** that converts spoken utterances into accurate, postable text **together with** **neural text-to-speech** that renders lines as natural, consistent audio—fast enough to feel usable during **live voice hangs**.

## What has Changed
Nothing has really shifted in **audience**, **problem**, **key differentiator**, or the **POWERED BY** line since the vision was first committed; our work stayed inside that framing (vendor-agnostic ASR/TTS in the statement, Deepgram in `apps/bot` today).