"""Voice-receive audio sink that buffers user speech and posts STT transcriptions."""

from __future__ import annotations

import asyncio
import audioop
import io
import logging
import os
import time
import wave
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord.ext import voice_recv

from apps.bot.content_moderation import (
    Disposition,
    format_sensitive_dm,
    moderate_for_transcript,
)
from apps.bot.transcription import AsrTranscriptionError, _agent_log, transcribe_audio

if TYPE_CHECKING:
    from apps.bot.transcription import AsrClient

LOGGER = logging.getLogger("ttstt-bot.stt")

_SAMPLE_RATE = 48_000
_CHANNELS = 2       # Discord delivers stereo PCM (both channels identical for a single speaker)
_SAMPLE_WIDTH = 2   # 16-bit signed LE
_ASR_CHANNELS = 1   # downmix to mono before sending to ASR — halves payload, avoids duplicate transcripts
SILENCE_TIMEOUT = 0.8  # seconds of silence before flushing an utterance
MIN_PCM_BYTES = int(_SAMPLE_RATE * _CHANNELS * _SAMPLE_WIDTH * 0.25)  # 250 ms minimum (stereo)


def _debug_save_wav_enabled() -> bool:
    return os.getenv("STT_DEBUG_SAVE_WAV", "").strip().lower() in {"1", "true", "yes", "on"}


def _save_debug_wav(
    *,
    guild_id: int,
    user_id: int,
    wav: bytes,
    pcm_peak: int,
) -> Path | None:
    """Write captured utterance WAV to disk when STT_DEBUG_SAVE_WAV is enabled."""

    if not _debug_save_wav_enabled():
        return None

    out_dir = Path(os.getenv("STT_DEBUG_WAV_DIR", "stt_debug_audio"))
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"guild{guild_id}_user{user_id}_{int(time.time() * 1000)}.wav"
    path.write_bytes(wav)
    LOGGER.info("STT debug WAV saved: %s (pcm_peak=%s bytes=%s)", path.resolve(), pcm_peak, len(wav))
    # #region agent log
    _agent_log(
        hypothesis_id="H7",
        location="stt.py:_save_debug_wav",
        message="Wrote debug WAV file",
        data={"path": str(path.resolve()), "pcm_peak": pcm_peak, "wav_bytes": len(wav)},
    )
    # #endregion
    return path


def _stereo_to_mono(pcm: bytes) -> bytes:
    """Extract the left channel of interleaved stereo 16-bit PCM.

    Discord delivers stereo PCM where L and R can be in anti-phase (L = -R) due to
    mid-side Opus coding or echo cancellation processing on the Discord server side.
    Averaging (0.5*L + 0.5*R) cancels anti-phase frames to silence, destroying the
    speech signal. Extracting just L avoids this regardless of L/R phase relationship.
    """
    return audioop.tomono(pcm, _SAMPLE_WIDTH, 1.0, 0.0)


def _wrap_pcm_as_wav(pcm: bytes, *, channels: int = _ASR_CHANNELS) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(_SAMPLE_WIDTH)
        wf.setframerate(_SAMPLE_RATE)
        wf.writeframes(pcm)
    buf.seek(0)
    return buf.read()


class _UserBuffer:
    __slots__ = ("pcm", "seq")

    def __init__(self) -> None:
        self.pcm: bytearray = bytearray()
        self.seq: int = 0

    def add(self, chunk: bytes) -> int:
        self.pcm.extend(chunk)
        self.seq += 1
        return self.seq

    def collect(self) -> bytes:
        data = bytes(self.pcm)
        self.pcm.clear()
        return data


class SttListenerRegistry:
    """Track which users' voices should be transcribed per guild."""

    def __init__(self) -> None:
        self._users: dict[int, set[int]] = defaultdict(set)

    def add(self, guild_id: int, user_id: int) -> None:
        self._users[guild_id].add(user_id)

    def remove(self, guild_id: int, user_id: int) -> bool:
        s = self._users.get(guild_id)
        if not s or user_id not in s:
            return False
        s.discard(user_id)
        return True

    def contains(self, guild_id: int, user_id: int) -> bool:
        return user_id in self._users.get(guild_id, set())

    def clear(self, guild_id: int) -> set[int]:
        return self._users.pop(guild_id, set())

    def list_users(self, guild_id: int) -> set[int]:
        return set(self._users.get(guild_id, set()))


class TranscriptionSink(voice_recv.AudioSink):
    """
    Buffers per-user PCM audio, detects utterance end via a silence timeout,
    transcribes with the injected ASR client, and posts to the control channel.

    write() is called from the voice-receive thread; all async work is
    scheduled onto the bot's event loop via run_coroutine_threadsafe.
    """

    def __init__(
        self,
        *,
        asr_client: AsrClient,
        listeners: SttListenerRegistry,
        guild_id: int,
        text_channel_id: int,
        openai_api_key: str | None = None,
    ) -> None:
        super().__init__()
        self._asr_client = asr_client
        self._listeners = listeners
        self._guild_id = guild_id
        self._text_channel_id = text_channel_id
        self._openai_api_key = openai_api_key
        self._buffers: dict[int, _UserBuffer] = {}

    def wants_opus(self) -> bool:
        return False

    def write(self, user: discord.User | None, data: voice_recv.VoiceData) -> None:
        if user is None or not self._listeners.contains(self._guild_id, user.id):
            return

        buf = self._buffers.setdefault(user.id, _UserBuffer())
        seq = buf.add(data.pcm)

        assert self.client is not None
        asyncio.run_coroutine_threadsafe(
            self._flush_after_silence(user, buf, seq),
            self.client.loop,
        )

    async def _flush_after_silence(
        self, user: discord.User, buf: _UserBuffer, seq: int
    ) -> None:
        await asyncio.sleep(SILENCE_TIMEOUT)
        if buf.seq != seq:
            return  # newer audio arrived since this timer was scheduled

        pcm = buf.collect()
        if len(pcm) < MIN_PCM_BYTES:
            # #region agent log
            _agent_log(
                hypothesis_id="H6",
                location="stt.py:_flush_after_silence:too_short",
                message="PCM below minimum",
                data={"pcm_bytes": len(pcm), "min_pcm_bytes": MIN_PCM_BYTES, "user_id": user.id},
            )
            # #endregion
            return

        pcm_peak = audioop.max(pcm, _SAMPLE_WIDTH)
        mono_pcm = _stereo_to_mono(pcm)
        wav = _wrap_pcm_as_wav(mono_pcm)
        _save_debug_wav(guild_id=self._guild_id, user_id=user.id, wav=wav, pcm_peak=pcm_peak)
        # #region agent log
        _agent_log(
            hypothesis_id="H7",
            location="stt.py:_flush_after_silence:flush",
            message="Flushing utterance to Deepgram",
            data={"user_id": user.id, "pcm_bytes": len(pcm), "wav_bytes": len(wav), "pcm_peak": pcm_peak},
        )
        # #endregion
        try:
            text = await asyncio.to_thread(transcribe_audio, wav, self._asr_client)
        except AsrTranscriptionError as exc:
            LOGGER.warning("STT failed for user=%s: %s", user.id, exc)
            return
        except Exception as exc:
            LOGGER.warning("Unexpected STT error for user=%s: %s", user.id, exc)
            return

        if not text:
            LOGGER.warning(
                "STT empty transcript for user=%s (pcm_bytes=%s pcm_peak=%s); check mic input and Deepgram key",
                user.id,
                len(pcm),
                pcm_peak,
            )
            # #region agent log
            _agent_log(
                hypothesis_id="H5",
                location="stt.py:_flush_after_silence:empty_transcript",
                message="Deepgram returned empty transcript",
                data={"user_id": user.id, "pcm_bytes": len(pcm), "pcm_peak": pcm_peak},
            )
            # #endregion
            return

        outcome = moderate_for_transcript(text, openai_api_key=self._openai_api_key)
        if outcome.disposition is Disposition.BLOCKED:
            LOGGER.info("Suppressed transcript for user=%s (%s)", user.id, outcome.log_reason)
            return

        if outcome.disposition is Disposition.PRIVATE_DM:
            dm_body = outcome.dm_body or text
            try:
                await user.send(
                    format_sensitive_dm(dm_body, outcome.crisis_footer),
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            except discord.Forbidden:
                LOGGER.warning("Sensitive transcript for user=%s could not be delivered via DM", user.id)
            return

        channel = self.client.get_channel(self._text_channel_id)  # type: ignore[union-attr]
        if not isinstance(channel, discord.TextChannel):
            try:
                channel = await self.client.fetch_channel(self._text_channel_id)  # type: ignore[union-attr]
            except discord.HTTPException:
                channel = None
        if not isinstance(channel, discord.TextChannel):
            LOGGER.warning("STT cannot resolve text channel %s", self._text_channel_id)
            # #region agent log
            _agent_log(
                hypothesis_id="H8",
                location="stt.py:_flush_after_silence:channel_missing",
                message="Text channel not found in cache",
                data={"text_channel_id": self._text_channel_id},
            )
            # #endregion
            return

        public_text = outcome.public_text or text
        await channel.send(
            f"**{user.display_name}**: {public_text}",
            allowed_mentions=discord.AllowedMentions.none(),
        )
        # #region agent log
        _agent_log(
            hypothesis_id="H8",
            location="stt.py:_flush_after_silence:posted",
            message="Posted transcript to channel",
            data={"text_channel_id": self._text_channel_id, "text_len": len(public_text)},
        )
        # #endregion

    def cleanup(self) -> None:
        self._buffers.clear()
