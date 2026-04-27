"""Discord voice-to-text relay bot entrypoint."""

from __future__ import annotations

import asyncio
import logging
import os
import time
from collections import deque
from dataclasses import dataclass

import discord
from discord import app_commands
from discord.ext import commands, voice_recv
from dotenv import load_dotenv

from bot.audio_pipeline import BufferedTranscriptionSink, pcm_to_wav
from bot.deepgram_client import DeepgramTranscriber
from bot.webhook_sender import ChannelWebhookSender

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("voice-relay-bot")


def _install_opus_decode_guard() -> None:
    """Prevent known corrupted Opus packets from crashing receive router threads."""

    if getattr(discord.opus.Decoder.decode, "_relay_guard_installed", False):
        return

    original_decode = discord.opus.Decoder.decode

    def guarded_decode(self: discord.opus.Decoder, data: bytes | None, *, fec: bool = False) -> bytes:
        try:
            return original_decode(self, data, fec=fec)
        except discord.opus.OpusError as exc:
            # Known voice-recv failure path: discard/conceal corrupted packets and continue.
            if "corrupted stream" not in str(exc).lower():
                raise
            try:
                return original_decode(self, None, fec=False)
            except Exception:
                return b""

    setattr(guarded_decode, "_relay_guard_installed", True)
    discord.opus.Decoder.decode = guarded_decode  # type: ignore[assignment]


@dataclass(slots=True)
class GuildSession:
    text_channel_id: int
    voice_client: voice_recv.VoiceRecvClient
    sink: BufferedTranscriptionSink | None


class RelayBot(commands.Bot):
    def __init__(self, discord_token: str, deepgram_api_key: str) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True

        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.discord_token = discord_token
        self.transcriber = DeepgramTranscriber(deepgram_api_key)
        self.sessions: dict[int, GuildSession] = {}
        self.webhooks: ChannelWebhookSender | None = None
        self._restart_timestamps: dict[int, deque[float]] = {}
        self._restart_in_progress: set[int] = set()

    async def setup_hook(self) -> None:
        self.tree.add_command(join_voice)
        self.tree.add_command(leave_voice)
        self.tree.add_command(relay_status)
        await self.tree.sync()

    async def on_ready(self) -> None:
        if self.user is None:
            return
        self.webhooks = ChannelWebhookSender(self.user.id)
        LOGGER.info("Bot ready as %s", self.user)

    async def close_session(self, guild_id: int) -> None:
        session = self.sessions.pop(guild_id, None)
        if session is None:
            return

        if session.sink is not None:
            await session.sink.stop()

        if session.voice_client.is_listening():
            session.voice_client.stop_listening()
        if session.voice_client.is_connected():
            await session.voice_client.disconnect(force=True)

        self._restart_timestamps.pop(guild_id, None)
        self._restart_in_progress.discard(guild_id)

    async def start_listening(self, guild_id: int) -> None:
        session = self.sessions.get(guild_id)
        if session is None:
            return

        sink = BufferedTranscriptionSink(segment_handler=lambda member, pcm: self.relay_segment(guild_id, member, pcm))
        await sink.start()

        def on_listen_end(error: Exception | None) -> None:
            if error is None:
                return
            LOGGER.warning("Voice receive ended with error; scheduling restart: %r", error)
            self.loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self.restart_listening_with_backoff(guild_id))
            )

        session.voice_client.listen(sink, after=on_listen_end)
        session.sink = sink

    async def restart_listening(self, guild_id: int) -> None:
        session = self.sessions.get(guild_id)
        if session is None:
            return
        if not session.voice_client.is_connected():
            return

        if session.sink is not None:
            await session.sink.stop()
            session.sink = None

        if session.voice_client.is_listening():
            session.voice_client.stop_listening()

        await asyncio.sleep(0.3)
        await self.start_listening(guild_id)

    async def restart_listening_with_backoff(self, guild_id: int) -> None:
        if guild_id in self._restart_in_progress:
            return

        session = self.sessions.get(guild_id)
        if session is None:
            return

        self._restart_in_progress.add(guild_id)
        try:
            now = time.monotonic()
            history = self._restart_timestamps.setdefault(guild_id, deque())
            history.append(now)
            while history and (now - history[0]) > 45.0:
                history.popleft()

            restart_count = len(history)
            if restart_count > 12:
                # Circuit breaker: stop runaway restart loops.
                await self.close_session(guild_id)
                channel = self.get_channel(session.text_channel_id)
                if isinstance(channel, discord.TextChannel):
                    await channel.send(
                        "Voice receive became unstable and has been stopped after repeated decoder failures. "
                        "Try restarting the bot with Python 3.11 and then run `/join` again."
                    )
                return

            backoff_s = min(8.0, 0.25 * (2 ** max(0, restart_count - 1)))
            await asyncio.sleep(backoff_s)
            await self.restart_listening(guild_id)
        finally:
            self._restart_in_progress.discard(guild_id)

    async def relay_segment(self, guild_id: int, member: discord.Member, pcm_chunk: bytes) -> None:
        session = self.sessions.get(guild_id)
        if session is None or self.webhooks is None:
            return

        channel = self.get_channel(session.text_channel_id)
        if not isinstance(channel, discord.TextChannel):
            return

        wav_bytes = pcm_to_wav(pcm_chunk)

        try:
            result = await self.transcriber.transcribe_wav(wav_bytes)
        except Exception:
            LOGGER.exception("Deepgram transcription failed")
            return

        if result is None:
            return

        try:
            await self.webhooks.send_as_member(channel, member, result.text)
        except Exception:
            LOGGER.exception("Failed to send transcript message")


async def _ensure_voice_recv_client(
    interaction: discord.Interaction,
    member: discord.Member,
) -> voice_recv.VoiceRecvClient:
    guild = interaction.guild
    assert guild is not None
    assert member.voice is not None

    existing = guild.voice_client
    if existing is None:
        return await member.voice.channel.connect(cls=voice_recv.VoiceRecvClient)

    if not isinstance(existing, voice_recv.VoiceRecvClient):
        await existing.disconnect(force=True)
        return await member.voice.channel.connect(cls=voice_recv.VoiceRecvClient)

    if existing.channel != member.voice.channel:
        await existing.move_to(member.voice.channel)

    return existing


@app_commands.command(name="join", description="Join your voice channel and start relaying transcripts.")
async def join_voice(interaction: discord.Interaction) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None or not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Use this command in a guild text channel.", ephemeral=True)
        return

    if not isinstance(interaction.user, discord.Member) or interaction.user.voice is None:
        await interaction.response.send_message("Join a voice channel first.", ephemeral=True)
        return

    me = interaction.guild.me
    if me is None:
        await interaction.response.send_message("I cannot resolve my guild member state.", ephemeral=True)
        return

    voice_perms = interaction.user.voice.channel.permissions_for(me)
    if not (voice_perms.connect and voice_perms.speak and voice_perms.view_channel):
        await interaction.response.send_message(
            "I need Connect, Speak, and View Channel permissions in that voice channel.",
            ephemeral=True,
        )
        return

    text_perms = interaction.channel.permissions_for(me)
    if not (text_perms.send_messages and text_perms.manage_webhooks):
        await interaction.response.send_message(
            "I need Send Messages and Manage Webhooks permissions in this text channel.",
            ephemeral=True,
        )
        return

    await bot.close_session(interaction.guild.id)

    try:
        voice_client = await _ensure_voice_recv_client(interaction, interaction.user)
    except Exception:
        LOGGER.exception("Failed to connect to voice channel")
        await interaction.response.send_message("Could not connect to your voice channel.", ephemeral=True)
        return

    bot.sessions[interaction.guild.id] = GuildSession(
        text_channel_id=interaction.channel.id,
        voice_client=voice_client,
        sink=None,
    )
    await bot.start_listening(interaction.guild.id)

    await interaction.response.send_message(
        f"Listening in {interaction.user.voice.channel.mention} and posting transcripts to {interaction.channel.mention}."
    )


@app_commands.command(name="leave", description="Stop relaying transcripts and leave voice.")
async def leave_voice(interaction: discord.Interaction) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None:
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    if interaction.guild.id not in bot.sessions:
        await interaction.response.send_message("I am not currently listening in this server.", ephemeral=True)
        return

    await bot.close_session(interaction.guild.id)
    await interaction.response.send_message("Stopped listening and disconnected.")


@app_commands.command(name="status", description="Show current relay status for this server.")
async def relay_status(interaction: discord.Interaction) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None:
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    session = bot.sessions.get(interaction.guild.id)
    if session is None:
        await interaction.response.send_message("Not listening right now.", ephemeral=True)
        return

    channel = bot.get_channel(session.text_channel_id)
    if isinstance(channel, discord.TextChannel):
        channel_desc = channel.mention
    else:
        channel_desc = f"<#{session.text_channel_id}>"

    voice_channel = session.voice_client.channel
    voice_desc = voice_channel.mention if isinstance(voice_channel, discord.VoiceChannel) else "unknown channel"

    await interaction.response.send_message(
        f"Listening in {voice_desc}; relaying transcripts to {channel_desc}.",
        ephemeral=True,
    )


async def main() -> None:
    load_dotenv()
    _install_opus_decode_guard()

    discord_token = os.getenv("DISCORD_TOKEN")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    if not discord_token or not deepgram_api_key:
        raise RuntimeError("DISCORD_TOKEN and DEEPGRAM_API_KEY must be set in .env.")

    bot = RelayBot(discord_token=discord_token, deepgram_api_key=deepgram_api_key)
    await bot.start(bot.discord_token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
