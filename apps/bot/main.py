"""Deployable Discord bot entrypoint with message-listener TTS support."""

from __future__ import annotations

import asyncio
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from apps.bot.content_moderation import Disposition, moderate_for_tts
from apps.bot.db import create_postgres_pool
from apps.bot.playback import PlaybackCoordinator
from apps.bot.session_registry import SessionRegistry
from apps.bot.piper_tts import PiperTtsClient, get_default_piper_voice
from apps.bot.tts import DeepgramTtsClient, TtsClient, TtsSynthesisError, chunk_text_for_tts, synthesize_text
from apps.bot.tts_listener_registry import TtsListenerRegistry
from apps.bot.voice_preferences import (
    FEATURED_AURA2_VOICES,
    FEATURED_PIPER_VOICES,
    PostgresVoicePreferencesRepository,
    TtsProvider,
    apply_tts_provider_switch,
    format_voice_settings_message,
    merge_voice_preferences,
)

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("ttstt-bot")

MAX_TTS_CHARS = 300
DEFAULT_HELP_URL = "https://csen-scu.github.io/csen-174-s26-team-project-ttstt/"


def _should_enqueue_message(
    *,
    control_channel_id: int | None,
    message_channel_id: int,
    author_is_bot: bool,
    guild_present: bool,
    is_listened_user: bool,
) -> bool:
    if author_is_bot or not guild_present:
        return False
    if control_channel_id is None or message_channel_id != control_channel_id:
        return False
    return is_listened_user


class RelayBot(commands.Bot):
    def __init__(
        self,
        discord_token: str,
        *,
        tts_deepgram: DeepgramTtsClient | None,
        tts_piper: PiperTtsClient | None,
        voice_preferences: PostgresVoicePreferencesRepository,
        db_pool: object,
        ffmpeg_executable: str,
        openai_api_key: str | None = None,
        help_url: str = DEFAULT_HELP_URL,
    ) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.discord_token = discord_token
        self.tts_deepgram = tts_deepgram
        self.tts_piper = tts_piper
        self.voice_preferences = voice_preferences
        self.db_pool = db_pool
        self.sessions = SessionRegistry()
        self.listeners = TtsListenerRegistry()
        self.playback = PlaybackCoordinator(bot=self, ffmpeg_executable=ffmpeg_executable)
        self.openai_api_key = openai_api_key
        self.help_url = help_url

    async def setup_hook(self) -> None:
        self.tree.add_command(join_voice)
        self.tree.add_command(leave_voice)
        self.tree.add_command(bot_status)
        self.tree.add_command(tts_listen_user)
        self.tree.add_command(tts_stop_listening_user)
        self.tree.add_command(tts_stop_all_listeners)
        self.tree.add_command(tts_provider_set)
        self.tree.add_command(tts_voice_set)
        self.tree.add_command(tts_voice_show)
        self.tree.add_command(tts_voice_reset)
        self.tree.add_command(help_command)
        await self.tree.sync()

    async def on_ready(self) -> None:
        if self.user is not None:
            LOGGER.info("Bot ready as %s", self.user)

    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        if not isinstance(message.author, discord.Member):
            return

        control_channel_id = self.sessions.get(message.guild.id)
        is_listened_user = self.listeners.contains(guild_id=message.guild.id, user_id=message.author.id)
        if not _should_enqueue_message(
            control_channel_id=control_channel_id,
            message_channel_id=message.channel.id,
            author_is_bot=message.author.bot,
            guild_present=message.guild is not None,
            is_listened_user=is_listened_user,
        ):
            return

        voice_client = message.guild.voice_client
        if voice_client is None or not voice_client.is_connected():
            return

        text = message.clean_content.strip()
        if not text:
            return

        moderation = moderate_for_tts(text, openai_api_key=self.openai_api_key)
        if moderation.disposition is Disposition.BLOCKED:
            LOGGER.info(
                "Suppressed TTS for guild=%s user=%s (%s)",
                message.guild.id,
                message.author.id,
                moderation.log_reason,
            )
            return

        text = moderation.public_text or text

        try:
            prefs = await self.voice_preferences.get(guild_id=message.guild.id, user_id=message.author.id)
        except Exception:
            LOGGER.exception(
                "Voice preferences lookup failed for guild=%s user=%s",
                message.guild.id,
                message.author.id,
            )
            return

        try:
            tts_client = self._resolve_tts_client(prefs.tts_provider)
        except TtsSynthesisError as exc:
            LOGGER.warning(
                "TTS provider unavailable for guild=%s user=%s provider=%s: %s",
                message.guild.id,
                message.author.id,
                prefs.tts_provider.value,
                exc,
            )
            return

        chunks = chunk_text_for_tts(text=text, max_chars=MAX_TTS_CHARS)
        for chunk in chunks:
            try:
                audio_bytes = await asyncio.to_thread(
                    synthesize_text,
                    chunk,
                    prefs.to_provider_dict(),
                    tts_client,
                )
            except TtsSynthesisError as exc:
                LOGGER.warning(
                    "TTS failed for guild=%s user=%s provider=%s: %s",
                    message.guild.id,
                    message.author.id,
                    prefs.tts_provider.value,
                    exc,
                )
                continue

            item = self.playback.enqueue(
                guild_id=message.guild.id,
                audio_bytes=audio_bytes,
                source_user_id=message.author.id,
                source_message_id=message.id,
            )
            LOGGER.info(
                "Queued TTS guild=%s user=%s seq=%s bytes=%s",
                message.guild.id,
                message.author.id,
                item.sequence_id,
                len(audio_bytes),
            )

    async def close(self) -> None:
        await self.playback.shutdown()
        maybe_close = getattr(self.db_pool, "close", None)
        if callable(maybe_close):
            close_result = maybe_close()
            if asyncio.iscoroutine(close_result):
                await close_result
        await super().close()

    def _resolve_tts_client(self, provider: TtsProvider) -> TtsClient:
        if provider is TtsProvider.PIPER:
            if self.tts_piper is None:
                raise TtsSynthesisError(
                    "Piper TTS is not configured on this bot. "
                    "Set PIPER_MODEL_DIR (and install piper), or run /tts_provider_set deepgram."
                )
            return self.tts_piper
        if self.tts_deepgram is None:
            raise TtsSynthesisError(
                "Deepgram TTS is not configured on this bot. "
                "Set DEEPGRAM_API_KEY, or run /tts_provider_set piper with Piper configured."
            )
        return self.tts_deepgram


async def _ensure_voice_client(
    interaction: discord.Interaction,
    member: discord.Member,
) -> discord.VoiceClient:
    guild = interaction.guild
    assert guild is not None
    assert member.voice is not None

    existing = guild.voice_client
    if existing is None:
        return await member.voice.channel.connect()

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

    await interaction.response.defer()

    try:
        voice_client = await _ensure_voice_client(interaction, interaction.user)
    except Exception:
        LOGGER.exception("Failed to connect to voice channel")
        await interaction.followup.send("Could not connect to your voice channel.", ephemeral=True)
        return

    bot.sessions.upsert(interaction.guild.id, interaction.channel.id)

    await interaction.followup.send(
        f"Connected to {voice_client.channel.mention if voice_client.channel else 'voice'} "
        f"from {interaction.channel.mention}.\n\n"
        "**Privacy:** Text from users you add with `/tts_listen_user` may be read aloud "
        "in voice after content safety checks."
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
    bot.listeners.clear(interaction.guild.id)
    bot.playback.clear_guild(interaction.guild.id)
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
    listener_count = len(bot.listeners.list_users(interaction.guild.id))
    await interaction.response.send_message(
        f"Connected in {voice_ref}; control channel is {text_ref}; listening to {listener_count} user(s).",
        ephemeral=True,
    )


@app_commands.command(name="tts_listen_user", description="Start reading messages from this user in voice.")
@app_commands.describe(user="User whose text messages should be read aloud")
async def tts_listen_user(interaction: discord.Interaction, user: discord.Member) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None or not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Use this command in a guild text channel.", ephemeral=True)
        return

    voice_client = interaction.guild.voice_client
    if voice_client is None or not voice_client.is_connected():
        await interaction.response.send_message("Run `/join` first so I am connected to voice.", ephemeral=True)
        return

    control_channel_id = bot.sessions.get(interaction.guild.id)
    if control_channel_id != interaction.channel.id:
        await interaction.response.send_message(
            "Use this command in the current control text channel (run `/join` here if needed).",
            ephemeral=True,
        )
        return

    bot.listeners.add(guild_id=interaction.guild.id, user_id=user.id)
    await interaction.response.send_message(f"Now listening to {user.mention} in this channel.", ephemeral=True)


@app_commands.command(name="tts_stop_listening_user", description="Stop reading messages from this user.")
@app_commands.describe(user="User to remove from TTS listening")
async def tts_stop_listening_user(interaction: discord.Interaction, user: discord.Member) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None:
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    removed = bot.listeners.remove(guild_id=interaction.guild.id, user_id=user.id)
    if not removed:
        await interaction.response.send_message(f"{user.mention} is not currently being listened to.", ephemeral=True)
        return
    await interaction.response.send_message(f"Stopped listening to {user.mention}.", ephemeral=True)


@app_commands.command(name="tts_stop_all_listeners", description="Stop reading messages from all users in this server.")
async def tts_stop_all_listeners(interaction: discord.Interaction) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None:
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    cleared = bot.listeners.clear(interaction.guild.id)
    bot.playback.clear_guild(interaction.guild.id)
    await interaction.response.send_message(
        f"Stopped listening to {len(cleared)} user(s) in this server.",
        ephemeral=True,
    )


@app_commands.command(
    name="tts_provider_set",
    description="Choose Deepgram Aura (cloud) or Piper (local) for your TTS in this server.",
)
@app_commands.describe(
    provider="TTS engine: deepgram (cloud) or piper (local ONNX voices)",
)
@app_commands.choices(
    provider=[
        app_commands.Choice(name="Deepgram Aura (cloud)", value=TtsProvider.DEEPGRAM.value),
        app_commands.Choice(name="Piper (local)", value=TtsProvider.PIPER.value),
    ]
)
async def tts_provider_set(
    interaction: discord.Interaction,
    provider: app_commands.Choice[str],
) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None or not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    try:
        selected = TtsProvider.parse(provider.value)
    except ValueError as exc:
        await interaction.response.send_message(str(exc), ephemeral=True)
        return

    if selected is TtsProvider.PIPER and bot.tts_piper is None:
        await interaction.response.send_message(
            "Piper is not configured on this bot (set PIPER_MODEL_DIR and install the piper binary).",
            ephemeral=True,
        )
        return
    if selected is TtsProvider.DEEPGRAM and bot.tts_deepgram is None:
        await interaction.response.send_message(
            "Deepgram is not configured on this bot (set DEEPGRAM_API_KEY).",
            ephemeral=True,
        )
        return

    current = await bot.voice_preferences.get(guild_id=interaction.guild.id, user_id=interaction.user.id)
    updated = apply_tts_provider_switch(current, selected)
    try:
        saved = await bot.voice_preferences.upsert(
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
            prefs=updated,
        )
    except ValueError as exc:
        await interaction.response.send_message(str(exc), ephemeral=True)
        return
    except Exception as exc:
        LOGGER.warning("Failed to persist TTS provider: %r", exc)
        await interaction.response.send_message(
            "Could not save TTS provider right now. Please try again.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        format_voice_settings_message(saved, prefix="TTS provider updated"),
        ephemeral=True,
    )


@app_commands.command(name="tts_voice_set", description="Set your TTS voice preferences in this server.")
@app_commands.describe(
    voice="Voice id for your provider (Aura model or Piper ONNX basename)",
    speed="Speech speed between 0.5 and 2.0",
    pitch="Pitch between -20 and 20",
    style="Optional style/tone label; use none to clear",
)
async def tts_voice_set(
    interaction: discord.Interaction,
    voice: str | None = None,
    speed: app_commands.Range[float, 0.5, 2.0] | None = None,
    pitch: app_commands.Range[float, -20.0, 20.0] | None = None,
    style: str | None = None,
) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None or not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    if voice is None and speed is None and pitch is None and style is None:
        await interaction.response.send_message(
            "Provide at least one option: voice, speed, pitch, or style "
            "(use style `none` to clear a saved style).",
            ephemeral=True,
        )
        return

    current = await bot.voice_preferences.get(guild_id=interaction.guild.id, user_id=interaction.user.id)
    merged = merge_voice_preferences(current, voice=voice, speed=speed, pitch=pitch, style=style)
    try:
        saved = await bot.voice_preferences.upsert(
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
            prefs=merged,
        )
    except ValueError as exc:
        await interaction.response.send_message(str(exc), ephemeral=True)
        return
    except Exception as exc:
        LOGGER.warning("Failed to persist TTS prefs: %r", exc)
        await interaction.response.send_message(
            "Could not save voice settings right now. Please try again.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        format_voice_settings_message(saved, prefix="Saved voice settings"),
        ephemeral=True,
    )


@tts_voice_set.autocomplete("voice")
async def tts_voice_set_voice_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    bot = interaction.client
    assert isinstance(bot, RelayBot)
    needle = (current or "").strip().lower()

    catalog: tuple[str, ...] = FEATURED_AURA2_VOICES
    if interaction.guild is not None and interaction.user is not None:
        prefs = await bot.voice_preferences.get(
            guild_id=interaction.guild.id,
            user_id=interaction.user.id,
        )
        if prefs.tts_provider is TtsProvider.PIPER:
            if bot.tts_piper is not None and bot.tts_piper.installed_voices:
                catalog = bot.tts_piper.installed_voices
            else:
                catalog = FEATURED_PIPER_VOICES

    matches = [v for v in catalog if needle in v.lower()]
    return [app_commands.Choice(name=model, value=model) for model in matches[:25]]


@app_commands.command(name="tts_voice_show", description="Show your TTS voice preferences in this server.")
async def tts_voice_show(interaction: discord.Interaction) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None or not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    prefs = await bot.voice_preferences.get(guild_id=interaction.guild.id, user_id=interaction.user.id)
    await interaction.response.send_message(
        format_voice_settings_message(prefs, prefix="Your voice settings"),
        ephemeral=True,
    )


@app_commands.command(name="tts_voice_reset", description="Reset your TTS voice preferences in this server.")
async def tts_voice_reset(interaction: discord.Interaction) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    if interaction.guild is None or not isinstance(interaction.user, discord.Member):
        await interaction.response.send_message("Use this command in a server.", ephemeral=True)
        return

    try:
        prefs = await bot.voice_preferences.reset(guild_id=interaction.guild.id, user_id=interaction.user.id)
    except Exception as exc:
        LOGGER.warning("Failed to reset TTS prefs: %r", exc)
        await interaction.response.send_message(
            "Could not reset voice settings right now. Please try again.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        format_voice_settings_message(prefs, prefix="Reset to defaults"),
        ephemeral=True,
    )


@app_commands.command(name="help", description="Open the TTSTT help guide in your browser.")
async def help_command(interaction: discord.Interaction) -> None:
    bot = interaction.client
    assert isinstance(bot, RelayBot)

    embed = discord.Embed(
        title="TTSTT Help",
        description=(
            "Full setup, commands, privacy, and troubleshooting:\n"
            f"[Open the help guide]({bot.help_url})"
        ),
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


def _build_tts_clients(*, deepgram_api_key: str | None, ffmpeg_executable: str) -> tuple[DeepgramTtsClient | None, PiperTtsClient | None]:
    tts_deepgram: DeepgramTtsClient | None = None
    if deepgram_api_key:
        tts_deepgram = DeepgramTtsClient(api_key=deepgram_api_key)

    tts_piper: PiperTtsClient | None = None
    piper_model_dir = os.getenv("PIPER_MODEL_DIR", "").strip()
    if piper_model_dir:
        tts_piper = PiperTtsClient(
            model_dir=piper_model_dir,
            executable=os.getenv("PIPER_EXECUTABLE", "piper"),
            default_voice=get_default_piper_voice(),
            ffmpeg_executable=ffmpeg_executable,
        )
    return tts_deepgram, tts_piper


async def main() -> None:
    load_dotenv()
    discord_token = os.getenv("DISCORD_TOKEN")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
    database_url = os.getenv("DATABASE_URL")
    ffmpeg_executable = os.getenv("FFMPEG_EXECUTABLE", "ffmpeg")
    help_url = os.getenv("HELP_URL", DEFAULT_HELP_URL)
    if not discord_token:
        raise RuntimeError("DISCORD_TOKEN must be set in .env.")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be set in .env.")

    tts_deepgram, tts_piper = _build_tts_clients(
        deepgram_api_key=deepgram_api_key,
        ffmpeg_executable=ffmpeg_executable,
    )
    if tts_deepgram is None and tts_piper is None:
        raise RuntimeError(
            "Configure at least one TTS backend: set DEEPGRAM_API_KEY and/or PIPER_MODEL_DIR in .env."
        )

    db_pool = await create_postgres_pool(database_url=database_url)
    bot = RelayBot(
        discord_token=discord_token,
        tts_deepgram=tts_deepgram,
        tts_piper=tts_piper,
        voice_preferences=PostgresVoicePreferencesRepository(conn=db_pool),
        db_pool=db_pool,
        ffmpeg_executable=ffmpeg_executable,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        help_url=help_url,
    )
    try:
        await bot.start(bot.discord_token)
    except discord.errors.PrivilegedIntentsRequired as exc:
        raise RuntimeError(
            "Discord privileged intent is disabled. Enable 'Message Content Intent' in the Discord Developer Portal "
            "for this application, then restart the bot."
        ) from exc
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
