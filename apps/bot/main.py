"""Deployable Discord bot entrypoint (voice join/leave only)."""

from __future__ import annotations

import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands, voice_recv
from dotenv import load_dotenv

from apps.bot.session_registry import SessionRegistry

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("ttstt-bot")


class RelayBot(commands.Bot):
    def __init__(self, discord_token: str) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True

        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.discord_token = discord_token
        self.sessions = SessionRegistry()

    async def setup_hook(self) -> None:
        self.tree.add_command(join_voice)
        self.tree.add_command(leave_voice)
        self.tree.add_command(bot_status)
        await self.tree.sync()

    async def on_ready(self) -> None:
        if self.user is not None:
            LOGGER.info("Bot ready as %s", self.user)


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
        f"from {interaction.channel.mention}.",
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

    text_channel_id = bot.sessions.get(interaction.guild.id)
    voice_client = interaction.guild.voice_client

    if text_channel_id is None or voice_client is None or not voice_client.is_connected():
        await interaction.response.send_message("Not connected right now.", ephemeral=True)
        return

    text_channel = bot.get_channel(text_channel_id)
    text_ref = text_channel.mention if isinstance(text_channel, discord.TextChannel) else f"<#{text_channel_id}>"
    voice_ref = voice_client.channel.mention if voice_client.channel else "unknown voice channel"
    await interaction.response.send_message(
        f"Connected in {voice_ref}; control channel is {text_ref}.",
        ephemeral=True,
    )


async def main() -> None:
    load_dotenv()
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        raise RuntimeError("DISCORD_TOKEN must be set in .env.")

    bot = RelayBot(discord_token=discord_token)
    await bot.start(bot.discord_token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
