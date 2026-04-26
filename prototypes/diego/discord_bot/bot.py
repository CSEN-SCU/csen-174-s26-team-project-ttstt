"""Discord prototype: Azure TTS reads slash-command text in the voice channel."""

from __future__ import annotations

import asyncio
import io
import os
import shutil
import time
import traceback
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from azure_tts import TTSError, synthesize_to_wav_bytes

# Same .env as the FastAPI overlay backend (gitignored).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# Optional: set to your server ID so slash commands sync immediately while testing.
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")
FFMPEG_EXECUTABLE = os.getenv("FFMPEG_EXECUTABLE", "ffmpeg")
MAX_TTS_CHARS = 2000


class TTSTTDiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self._audio_queue: asyncio.Queue[tuple[int, bytes]] = asyncio.Queue()
        self._player_task: asyncio.Task[None] | None = None

    async def setup_hook(self) -> None:
        await self._register_commands()
        if DISCORD_GUILD_ID:
            guild_obj = discord.Object(id=int(DISCORD_GUILD_ID))
            try:
                # Commands are declared globally; copy them into this guild for fast dev sync.
                self.tree.copy_global_to(guild=guild_obj)
                await self.tree.sync(guild=guild_obj)
                print(f"Synced slash commands to guild {DISCORD_GUILD_ID}.")
            except discord.Forbidden:
                print(
                    f"Missing access to guild {DISCORD_GUILD_ID}. "
                    "Falling back to global command sync."
                )
                await self.tree.sync()
        else:
            await self.tree.sync()

    async def on_ready(self) -> None:
        assert self.user is not None
        print(f"Logged in as {self.user} ({self.user.id})")
        ffmpeg_path = shutil.which(FFMPEG_EXECUTABLE)
        print(
            f"FFmpeg executable setting: {FFMPEG_EXECUTABLE}; "
            f"resolved path: {ffmpeg_path or 'NOT FOUND'}"
        )
        if self._player_task is None or self._player_task.done():
            self._player_task = asyncio.create_task(self._audio_player_worker())

    async def _register_commands(self) -> None:
        @self.tree.command(name="join", description="Join the voice channel you are in.")
        async def join(interaction: discord.Interaction) -> None:
            if not interaction.guild:
                await interaction.response.send_message(
                    "This command only works in a server.", ephemeral=True
                )
                return
            member = interaction.user
            if not isinstance(member, discord.Member):
                await interaction.response.send_message(
                    "Could not resolve member.", ephemeral=True
                )
                return
            if member.voice is None or member.voice.channel is None:
                await interaction.response.send_message(
                    "Join a voice channel first, then run `/join`.", ephemeral=True
                )
                return
            channel = member.voice.channel
            assert isinstance(channel, discord.VoiceChannel | discord.StageChannel)
            voice = interaction.guild.voice_client
            try:
                if voice is not None:
                    await voice.move_to(channel)
                else:
                    await channel.connect()
            except discord.ClientException as e:
                await interaction.response.send_message(
                    f"Could not connect to voice: {e}", ephemeral=True
                )
                return
            await interaction.response.send_message(f"Joined **{channel.name}**.")

        @self.tree.command(name="leave", description="Leave the voice channel.")
        async def leave(interaction: discord.Interaction) -> None:
            if not interaction.guild or interaction.guild.voice_client is None:
                await interaction.response.send_message(
                    "Not connected to a voice channel.", ephemeral=True
                )
                return
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Left voice channel.")

        @self.tree.command(name="say", description="Speak text in the voice channel (Azure TTS).")
        @app_commands.describe(message="What the bot should say aloud")
        async def say(interaction: discord.Interaction, message: str) -> None:
            if not interaction.guild:
                await interaction.response.send_message(
                    "This command only works in a server.", ephemeral=True
                )
                return
            vc = interaction.guild.voice_client
            if vc is None or not vc.is_connected():
                await interaction.response.send_message(
                    "Use `/join` from a voice channel first.", ephemeral=True
                )
                return
            if len(message) > MAX_TTS_CHARS:
                await interaction.response.send_message(
                    f"Message too long (max {MAX_TTS_CHARS} characters).", ephemeral=True
                )
                return

            await interaction.response.defer(ephemeral=True)
            try:
                print(
                    f"/say request guild={interaction.guild.id} "
                    f"user={interaction.user.id} chars={len(message)}"
                )
                started = time.perf_counter()
                # Azure SDK call is blocking; run it off the event loop
                # so Discord gateway heartbeats and voice websocket stay healthy.
                wav_bytes = await asyncio.to_thread(synthesize_to_wav_bytes, message)
                elapsed = time.perf_counter() - started
                print(
                    f"Azure TTS success guild={interaction.guild.id} "
                    f"bytes={len(wav_bytes)} elapsed_s={elapsed:.2f}"
                )
            except TTSError as e:
                print(f"Azure TTS failed: {e}")
                await interaction.followup.send(f"TTS failed: {e}", ephemeral=True)
                return
            except Exception:
                traceback.print_exc()
                await interaction.followup.send(
                    "TTS failed with an unexpected error.", ephemeral=True
                )
                return

            await self._audio_queue.put((interaction.guild.id, wav_bytes))
            print(
                f"Queued audio guild={interaction.guild.id} "
                f"queue_size={self._audio_queue.qsize()}"
            )
            await interaction.followup.send("Queued for playback.", ephemeral=True)

    async def _audio_player_worker(self) -> None:
        while not self.is_closed():
            try:
                guild_id, wav_bytes = await asyncio.wait_for(
                    self._audio_queue.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue

            try:
                guild = self.get_guild(guild_id)
                vc = guild.voice_client if guild else None
                if vc is None or not vc.is_connected():
                    print(f"Dropped audio for guild={guild_id}: voice client not connected")
                    continue

                print(f"Starting playback guild={guild_id} bytes={len(wav_bytes)}")
                source = discord.FFmpegPCMAudio(
                    source=io.BytesIO(wav_bytes),
                    pipe=True,
                    executable=FFMPEG_EXECUTABLE,
                    options="-loglevel error",
                )
                done = asyncio.Event()

                def after_play(err: BaseException | None) -> None:
                    if err:
                        print(f"Playback error: {err}")
                    else:
                        print(f"Playback finished guild={guild_id}")
                    self.loop.call_soon_threadsafe(done.set)

                vc.play(source, after=after_play)
                await done.wait()
            except Exception:
                traceback.print_exc()
            finally:
                self._audio_queue.task_done()


def main() -> None:
    if not DISCORD_TOKEN:
        raise SystemExit(
            "Set DISCORD_BOT_TOKEN in prototypes/diego/.env (see .env.example)."
        )
    bot = TTSTTDiscordBot()
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
