# Ethics Reflection — TTSTT

## Product Vision

**FOR** Discord communities, accessibility-minded guilds, and teams that already live in text and voice channels

**WHO** need accessible participation from people who are hard of hearing or Deaf and anyone in noisy environments or on low-quality gear where clean speech isn't reliable

**TTSTT** (Text To Speech To Text)

**IS A** Discord bot that sits in your server's voice and text channels

**THAT** reads written chat aloud in voice with each user's chosen synthetic voice (model, pacing, expressiveness, pitch, and speed)

**UNLIKE** using Discord alone, long text doesn't speak to the VC, or unlike expecting everyone to migrate to a single VC stack just to get basic bridging,

**OUR PRODUCT** meets people on Discord, uses slash and chat commands as the primary interface, and runs speech AI on infrastructure you control (API + Postgres)

**POWERED BY** neural text-to-speech that renders lines as natural, consistent audio, fast enough to feel usable during live voice hangs.

## Stakeholders (one user, one non-user)

### User Group

A user group is someone using the bot to speak their messages.

### Non-User Group

A non-user group is people in the voice call who are not using the bot but listening to the bot's messages being said aloud.

## Potential Harms

### 1.

**Harm:** A possible harm is if the generated voice does not pronounce a word how the user expects it to be pronounced.

**Principle:** 1.03 Approve software only if they have a well-founded belief that it is safe, meets specifications, passes appropriate tests, and does not diminish quality of life, diminish privacy, or harm the environment. The ultimate effect of the work should be to the public good.

**Mitigation:** We have already created the ability to set the pitch and speed of sentences, but not specific pronunciation. The user can try typing the word spelled differently to fix this.

### 2.

**Harm:** If a user wants to share sensitive information in the voice chat but not in the text chat, they have no way of doing that.

**Principle:** 1.04 Disclose to appropriate persons or authorities any actual or potential danger to the user, the public, or the environment, that they reasonably believe to be associated with software or related documents

**Mitigation:** There is no way of fixing this without completely reconstructing how the bot functions. We made this program with the assumption that because it is an accessibility tool, people will be generally patient and understanding with people who are using it.

### 3.

**Harm:** Someone could turn off the ability for the bot to listen to another user.

**Principle:** 1.03 Approve software only if they have a well-founded belief that it is safe, meets specifications, passes appropriate tests, and does not diminish quality of life, diminish privacy, or harm the environment. The ultimate effect of the work should be to the public good.

**Mitigation:** We can implement only having users be able to affect themselves with the bot commands. This is essential for ensuring the accessibility our product aims to achieve.

## Positive Impact

Our product creates value for mute or non-verbal users. Currently, the tools available to them are either paid or only work in certain situations, and if they wanted to use it in Discord, would have to use a workaround. This also has the added benefit of being useful to people who are in crowded rooms that might be noisy on a voice call. They would not have to unmute themselves to speak or find a different environment to participate in the call.

## One Concrete Change

We have already added the disclaimer in the UI to notify the user right when they load in the bot that whatever they type will be said aloud in the voice chat and written in the text chat. This was based on our ethical reasoning because we wanted to be clear about our product and how to use it safely, so that users are aware of the risks. We believe that this is enough for this product because we are assuming that if users are typing sensitive content, they intend to share it with others in the channel.

Another specific decision we will make before demo night is to add the functionality that users can only turn off the ability for the bot to listen to themselves, not others. This was based on our ethical reasoning because we are focused on accessibility, and we want to ensure that nobody can affect your ability to speak with others in the voice chat.
