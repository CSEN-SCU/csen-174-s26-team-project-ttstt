"""Deployable Discord bot entrypoint with ElevenLabs TTS."""

from __future__ import annotations

import asyncio
import logging
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands, voice_recv
from dotenv import load_dotenv

from apps.bot.audio_player import GuildAudioPlayer
from apps.bot.command_sync import sync_app_commands
from apps.bot.config import BotConfig, load_bot_config
from apps.bot.elevenlabs_client import ElevenLabsTtsClient, ElevenLabsTtsError
from apps.bot.session_registry import SessionRegistry
from apps.bot.tts import (
    TtsClient,
    chunk_text_for_tts,
    load_default_voice_prefs_from_env,
    synthesize_text,
)

__all__ = ["RelayBot", "sync_app_commands", "main"]

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("ttstt-bot")


class RelayBot(commands.Bot):
    def __init__(
        self,
        config: BotConfig,
        tts_client: TtsClient,
        default_voice_prefs: dict,
    ) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.config = config
        self.sessions = SessionRegistry()
        self.tts_client = tts_client
        self.default_voice_prefs = default_voice_prefs
        self.audio_player = GuildAudioPlayer(self, ffmpeg_executable=config.ffmpeg_executable)

    async def setup_hook(self) -> None:
        self.tree.add_command(join_voice)
        self.tree.add_command(leave_voice)
        self.tree.add_command(bot_status)
        self.tree.add_command(say_message)
        self.tree.add_command(relay_toggle)
        await sync_app_commands(self.tree, self.config.discord_guild_id)

    async def on_ready(self) -> None:
        if self.user is not None:
            LOGGER.info("Bot ready as %s", self.user)

    async def on_message(self, message: discord.Message) -> None:
        await self.process_commands(message)

        if message.author.bot or message.guild is None or not message.content:
            return

        bound_channel_id = self.sessions.get(message.guild.id)
        if bound_channel_id is None or bound_channel_id != message.channel.id:
            return
        if not self.sessions.is_relay_enabled(message.guild.id):
            return

        voice_client = message.guild.voice_client
        if voice_client is None or not voice_client.is_connected():
            return

        text = message.clean_content.strip()
        if not text:
            return
        if len(text) > self.config.tts_max_chars_per_message:
            text = text[: self.config.tts_max_chars_per_message]
            LOGGER.info("Truncated relay message for guild=%s", message.guild.id)

        try:
            await self._synthesize_and_enqueue(message.guild.id, text)
        except ElevenLabsTtsError:
            LOGGER.exception("Auto-relay synthesis failed for guild=%s", message.guild.id)
        except Exception:
            LOGGER.exception("Unexpected auto-relay failure for guild=%s", message.guild.id)

    async def _synthesize_and_enqueue(self, guild_id: int, text: str) -> None:
        chunks = chunk_text_for_tts(text, self.config.tts_max_chars_per_chunk)
        for chunk in chunks:
            audio = await asyncio.to_thread(
                synthesize_text, chunk, self.default_voice_prefs, self.tts_client
            )
            await self.audio_player.enqueue(guild_id, audio)

    async def close(self) -> None:
        await self.audio_player.shutdown()
        await super().close()


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


@app_commands.command(name="join", description="Join your voice channel.")
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

    try:
        voice_client = await _ensure_voice_recv_client(interaction, interaction.user)
    except Exception:
        LOGGER.exception("Failed to connect to voice channel")
        await interaction.response.send_message("Could not connect to your voice channel.", ephemeral=True)
        return

    bot.sessions.upsert(interaction.guild.id, interaction.channel.id)
    await interaction.response.send_message(
        f"Connected to {voice_client.channel.mention if voice_client.channel else 'voice'} "
        f"from {interaction.channel.mention}. Use `/say` or enable `/relay on` to read chat aloud.",
    )


@app_commands.command(name="leave", description="Leave voice channel for this server.")
async def leave_voice(interaction: discord.Interaction) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None:
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    voice_client = interaction.guild.voice_client
    if voice_client is None or not voice_client.is_connected():
        await interaction.response.send_message("I am not connected to voice right now.", ephemeral=True)
        return

    bot.sessions.remove(interaction.guild.id)
    await voice_client.disconnect(force=True)
    await interaction.response.send_message("Disconnected from voice.")


@app_commands.command(name="status", description="Show bot voice status for this server.")
async def bot_status(interaction: discord.Interaction) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None:
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    state = bot.sessions.get_state(interaction.guild.id)
    voice_client = interaction.guild.voice_client

    if state is None or voice_client is None or not voice_client.is_connected():
        await interaction.response.send_message("Not connected right now.", ephemeral=True)
        return

    text_channel = bot.get_channel(state.text_channel_id)
    text_ref = text_channel.mention if isinstance(text_channel, discord.TextChannel) else f"<#{state.text_channel_id}>"
    voice_ref = voice_client.channel.mention if voice_client.channel else "unknown voice channel"
    relay_ref = "on" if state.relay_enabled else "off"
    await interaction.response.send_message(
        f"Connected in {voice_ref}; control channel is {text_ref}; auto-relay is {relay_ref}.",
        ephemeral=True,
    )


@app_commands.command(name="say", description="Read a message aloud in the voice channel.")
@app_commands.describe(message="What the bot should say aloud.")
async def say_message(interaction: discord.Interaction, message: str) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None:
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    voice_client = interaction.guild.voice_client
    if voice_client is None or not voice_client.is_connected():
        await interaction.response.send_message("Use `/join` from a voice channel first.", ephemeral=True)
        return

    text = message.strip()
    if not text:
        await interaction.response.send_message("Message is empty.", ephemeral=True)
        return
    if len(text) > bot.config.tts_max_chars_per_message:
        await interaction.response.send_message(
            f"Message too long (max {bot.config.tts_max_chars_per_message} characters).",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True)
    try:
        await bot._synthesize_and_enqueue(interaction.guild.id, text)
    except ElevenLabsTtsError as exc:
        LOGGER.warning("TTS provider failure for guild=%s: %s", interaction.guild.id, exc)
        await interaction.followup.send(f"Text-to-speech failed: {exc}", ephemeral=True)
        return
    except Exception:
        LOGGER.exception("Unexpected /say failure for guild=%s", interaction.guild.id)
        await interaction.followup.send("Text-to-speech failed with an unexpected error.", ephemeral=True)
        return

    await interaction.followup.send("Queued for playback.", ephemeral=True)


@app_commands.command(name="relay", description="Auto-read chat messages in voice. Requires /join first.")
@app_commands.describe(state="Turn auto-relay on or off for this server.")
async def relay_toggle(
    interaction: discord.Interaction,
    state: Literal["on", "off"],
) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None:
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    enabled = state == "on"
    if not bot.sessions.set_relay(interaction.guild.id, enabled):
        await interaction.response.send_message(
            "Run `/join` from a voice channel first.", ephemeral=True
        )
        return

    if enabled:
        await interaction.response.send_message(
            "Auto-relay is on. Messages posted in this channel will be read in voice.",
        )
    else:
        await interaction.response.send_message("Auto-relay is off.")


async def main() -> None:
    load_dotenv()
    config = load_bot_config()
    tts_client = ElevenLabsTtsClient(
        api_key=config.elevenlabs_api_key,
        default_voice_id=config.elevenlabs_voice_id,
        default_model_id=config.elevenlabs_model_id,
    )
    voice_prefs = load_default_voice_prefs_from_env()

    bot = RelayBot(config=config, tts_client=tts_client, default_voice_prefs=voice_prefs)
    await bot.start(config.discord_token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
