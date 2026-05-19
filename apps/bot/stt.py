"""Voice-receive audio sink that buffers user speech and posts STT transcriptions."""

from __future__ import annotations

import array
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
MIN_PCM_BYTES = int(_SAMPLE_RATE * _CHANNELS * _SAMPLE_WIDTH * 1.0)  # 1 s minimum (stereo)
MAX_UTTERANCE_SEC = float(os.getenv("STT_MAX_UTTERANCE_SEC", "8"))
MAX_PCM_BYTES = int(_SAMPLE_RATE * _CHANNELS * _SAMPLE_WIDTH * MAX_UTTERANCE_SEC)
SILENCE_RMS_THRESHOLD = int(os.getenv("STT_SILENCE_RMS", "450"))
# Attenuate hot mic input before it hard-clips in the PCM buffer (peak 32768).
_INGRESS_PEAK_LIMIT = int(os.getenv("STT_INGRESS_PEAK", "8000"))
_ANTIPHASE_FORCE_SIDE_RATIO = float(os.getenv("STT_ANTIPHASE_RATIO", "0.35"))
_USE_OPUS_BUFFER = os.getenv("STT_OPUS_BUFFER", "1").strip().lower() not in {"0", "false", "no", "off"}
# Discord voice PCM frame: 20 ms @ 48 kHz stereo 16-bit
_PCM_FRAME_BYTES = int(_SAMPLE_RATE / 50) * _CHANNELS * _SAMPLE_WIDTH
_MAX_OPUS_FRAMES = int(MAX_UTTERANCE_SEC / 0.02) + 1


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


def _antiphase_fraction(pcm: bytes, *, max_samples: int = 12_000) -> float:
    """Share of stereo frames where L and R have opposite sign (mid-side / garble indicator)."""
    samples = array.array("h")
    samples.frombytes(pcm[: max_samples * _CHANNELS * _SAMPLE_WIDTH])
    if len(samples) < 4:
        return 0.0
    pairs = min(len(samples) // 2, max_samples)
    opposite = sum(1 for i in range(0, pairs * 2, 2) if samples[i] * samples[i + 1] < 0)
    return opposite / pairs


def _soft_limit_stereo_audio(pcm: bytes) -> bytes:
    """Reduce gain on stereo PCM so hot mics do not saturate at int16 max (peak 32768)."""
    peak = audioop.max(pcm, _SAMPLE_WIDTH)
    if peak <= _INGRESS_PEAK_LIMIT:
        return pcm
    return audioop.mul(pcm, _SAMPLE_WIDTH, _INGRESS_PEAK_LIMIT / peak)


def _decode_opus_frames(frames: list[bytes]) -> bytes:
    """Decode buffered Opus packets with a fresh decoder (avoids cross-utterance state)."""
    from discord.opus import OPUS_SILENCE, Decoder

    decoder = Decoder()
    parts: list[bytes] = []
    for frame in frames:
        if not frame or frame == OPUS_SILENCE:
            continue
        try:
            parts.append(decoder.decode(frame, fec=False))
        except Exception:
            LOGGER.debug("Skipping corrupt Opus frame during STT decode", exc_info=True)
    return b"".join(parts)


def _downmix_variants(pcm: bytes) -> list[tuple[bytes, str]]:
    """Build mono downmix candidates; order prefers side when channels are anti-phase."""
    sw = _SAMPLE_WIDTH
    left = audioop.tomono(pcm, sw, 1.0, 0.0)
    right = audioop.tomono(pcm, sw, 0.0, 1.0)
    mid = audioop.tomono(pcm, sw, 0.5, 0.5)
    side = audioop.tomono(pcm, sw, 0.5, -0.5)
    variants: dict[str, bytes] = {"mid": mid, "side": side, "L": left, "R": right}
    antiphase = _antiphase_fraction(pcm)
    if antiphase >= _ANTIPHASE_FORCE_SIDE_RATIO:
        order = ("side", "L", "R", "mid")
    else:
        rms = {name: audioop.rms(chunk, sw) for name, chunk in variants.items()}
        order = tuple(sorted(variants, key=lambda name: rms[name], reverse=True))
    seen: set[str] = set()
    out: list[tuple[bytes, str]] = []
    for name in order:
        if name in seen:
            continue
        seen.add(name)
        out.append((variants[name], name))
    return out


def _stereo_to_mono(pcm: bytes) -> tuple[bytes, str]:
    """Pick the best mono downmix for ASR (first entry in ranked variants)."""
    variants = _downmix_variants(pcm)
    return variants[0]


_NORMALIZE_TARGET_PEAK = 24000  # ~73% of 32767 — leaves headroom without over-compressing


def _normalize_pcm(pcm: bytes) -> bytes:
    """Scale PCM down to _NORMALIZE_TARGET_PEAK if the peak exceeds it.

    Does not restore already-clipped audio, but ensures Deepgram receives audio at a
    consistent amplitude and avoids any internal AGC issues from very loud input.
    """
    peak = audioop.max(pcm, _SAMPLE_WIDTH)
    if peak > _NORMALIZE_TARGET_PEAK:
        factor = _NORMALIZE_TARGET_PEAK / peak
        return audioop.mul(pcm, _SAMPLE_WIDTH, factor)
    return pcm


def _wrap_pcm_as_wav(pcm: bytes, *, channels: int = _ASR_CHANNELS) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(_SAMPLE_WIDTH)
        wf.setframerate(_SAMPLE_RATE)
        wf.writeframes(pcm)
    buf.seek(0)
    return buf.read()


def _is_mostly_silent_pcm(chunk: bytes) -> bool:
    """Drop near-empty Opus decode frames (Craig-style; common on some voice servers)."""
    if not chunk:
        return True
    if audioop.max(chunk, _SAMPLE_WIDTH) == 0:
        return True
    return audioop.rms(chunk, _SAMPLE_WIDTH) < 32


class _UserBuffer:
    __slots__ = ("pcm", "opus_frames", "seq", "last_speech_at", "use_opus")

    def __init__(self, *, use_opus: bool) -> None:
        self.use_opus = use_opus
        self.pcm: bytearray = bytearray()
        self.opus_frames: list[bytes] = []
        self.seq: int = 0
        self.last_speech_at: float = time.monotonic()

    def add_pcm(self, chunk: bytes) -> tuple[int, bool]:
        if _is_mostly_silent_pcm(chunk):
            self.seq += 1
            return self.seq, False
        chunk = _soft_limit_stereo_audio(chunk)
        self.pcm.extend(chunk)
        self.seq += 1
        if audioop.rms(chunk, _SAMPLE_WIDTH) >= SILENCE_RMS_THRESHOLD:
            self.last_speech_at = time.monotonic()
        at_cap = len(self.pcm) >= MAX_PCM_BYTES
        return self.seq, at_cap

    def add_opus(self, frame: bytes) -> tuple[int, bool]:
        from discord.opus import OPUS_SILENCE

        if not frame or frame == OPUS_SILENCE:
            self.seq += 1
            return self.seq, False
        self.opus_frames.append(frame)
        self.seq += 1
        self.last_speech_at = time.monotonic()
        at_cap = len(self.opus_frames) >= _MAX_OPUS_FRAMES
        return self.seq, at_cap

    def collect(self) -> tuple[bytes, str]:
        if self.use_opus:
            pcm = _decode_opus_frames(self.opus_frames)
            self.opus_frames.clear()
            source = "opus"
        else:
            pcm = bytes(self.pcm)
            self.pcm.clear()
            source = "pcm"
        self.last_speech_at = time.monotonic()
        pcm = _soft_limit_stereo_audio(pcm)
        return pcm, source

    def silent_long_enough(self) -> bool:
        return (time.monotonic() - self.last_speech_at) >= SILENCE_TIMEOUT


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
        return _USE_OPUS_BUFFER

    def write(self, user: discord.User | None, data: voice_recv.VoiceData) -> None:
        if user is None or not self._listeners.contains(self._guild_id, user.id):
            return

        buf = self._buffers.setdefault(
            user.id, _UserBuffer(use_opus=_USE_OPUS_BUFFER)
        )
        if _USE_OPUS_BUFFER:
            opus = data.opus
            if not opus:
                return
            seq, force_max = buf.add_opus(opus)
            has_audio = bool(buf.opus_frames)
        else:
            if not data.pcm:
                return
            seq, force_max = buf.add_pcm(data.pcm)
            has_audio = bool(buf.pcm)
        if not has_audio and not force_max:
            return

        assert self.client is not None
        loop = self.client.loop
        if force_max:
            asyncio.run_coroutine_threadsafe(
                self._flush_utterance(user, buf, seq, reason="max_duration"),
                loop,
            )
        asyncio.run_coroutine_threadsafe(
            self._flush_after_silence(user, buf, seq),
            loop,
        )

    async def _flush_after_silence(
        self, user: discord.User, buf: _UserBuffer, seq: int
    ) -> None:
        await asyncio.sleep(SILENCE_TIMEOUT)
        if buf.seq != seq:
            return
        if not buf.silent_long_enough():
            return
        await self._flush_utterance(user, buf, seq, reason="silence")

    async def _flush_utterance(
        self,
        user: discord.User,
        buf: _UserBuffer,
        seq: int,
        *,
        reason: str,
    ) -> None:
        if buf.seq != seq:
            return

        pcm, audio_source = buf.collect()
        if len(pcm) < MIN_PCM_BYTES:
            # #region agent log
            _agent_log(
                hypothesis_id="H6",
                location="stt.py:_flush_utterance:too_short",
                message="PCM below minimum",
                data={"pcm_bytes": len(pcm), "min_pcm_bytes": MIN_PCM_BYTES, "user_id": user.id},
            )
            # #endregion
            return

        pcm_peak = audioop.max(pcm, _SAMPLE_WIDTH)
        antiphase = _antiphase_fraction(pcm)
        if pcm_peak >= 32700:
            LOGGER.warning(
                "STT audio is clipping (peak=%s) for user=%s — "
                "lower microphone gain in Discord Settings → Voice & Video → Input Sensitivity",
                pcm_peak,
                user.id,
            )

        downmix_variants = _downmix_variants(pcm)
        text = ""
        downmix_mode = downmix_variants[0][1] if downmix_variants else "none"
        wav_bytes = 0
        mono_peak = 0
        winning_wav: bytes | None = None
        modes_tried: list[str] = []
        for mono_pcm, mode in downmix_variants:
            modes_tried.append(mode)
            normalized = _normalize_pcm(mono_pcm)
            wav = _wrap_pcm_as_wav(normalized)
            try:
                candidate = await asyncio.to_thread(transcribe_audio, wav, self._asr_client)
            except AsrTranscriptionError as exc:
                LOGGER.warning("STT failed for user=%s (%s): %s", user.id, mode, exc)
                continue
            except Exception as exc:
                LOGGER.warning("Unexpected STT error for user=%s (%s): %s", user.id, mode, exc)
                continue
            if candidate:
                text = candidate
                downmix_mode = mode
                wav_bytes = len(wav)
                mono_peak = audioop.max(normalized, _SAMPLE_WIDTH)
                winning_wav = wav
                break
            # #region agent log
            _agent_log(
                hypothesis_id="H5",
                location="stt.py:_flush_utterance:retry_downmix",
                message="Empty transcript; trying next downmix",
                data={"user_id": user.id, "downmix_mode": mode, "antiphase": round(antiphase, 3)},
            )
            # #endregion

        if winning_wav is not None:
            _save_debug_wav(
                guild_id=self._guild_id, user_id=user.id, wav=winning_wav, pcm_peak=pcm_peak
            )
        elif downmix_variants:
            first = _normalize_pcm(downmix_variants[0][0])
            _save_debug_wav(
                guild_id=self._guild_id,
                user_id=user.id,
                wav=_wrap_pcm_as_wav(first),
                pcm_peak=pcm_peak,
            )

        # #region agent log
        _agent_log(
            hypothesis_id="H7",
            location="stt.py:_flush_utterance:flush",
            message="Flushing utterance to Deepgram",
            data={
                "user_id": user.id,
                "pcm_bytes": len(pcm),
                "wav_bytes": wav_bytes,
                "pcm_peak": pcm_peak,
                "mono_peak_after_norm": mono_peak,
                "was_clipping": pcm_peak >= 32700,
                "downmix_mode": downmix_mode,
                "modes_tried": modes_tried,
                "antiphase": round(antiphase, 3),
                "audio_source": audio_source,
                "opus_buffer": _USE_OPUS_BUFFER,
                "flush_reason": reason,
                "utterance_sec": round(len(pcm) / (_SAMPLE_RATE * _CHANNELS * _SAMPLE_WIDTH), 2),
                "transcript_len": len(text),
            },
        )
        # #endregion

        if not text:
            LOGGER.warning(
                "STT empty transcript for user=%s (pcm_bytes=%s pcm_peak=%s modes=%s); "
                "check mic gain and Deepgram key",
                user.id,
                len(pcm),
                pcm_peak,
                modes_tried,
            )
            # #region agent log
            _agent_log(
                hypothesis_id="H5",
                location="stt.py:_flush_utterance:empty_transcript",
                message="Deepgram returned empty transcript",
                data={
                    "user_id": user.id,
                    "pcm_bytes": len(pcm),
                    "pcm_peak": pcm_peak,
                    "modes_tried": modes_tried,
                    "antiphase": round(antiphase, 3),
                    "audio_source": audio_source,
                },
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
                location="stt.py:_flush_utterance:channel_missing",
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
            location="stt.py:_flush_utterance:posted",
            message="Posted transcript to channel",
            data={"text_channel_id": self._text_channel_id, "text_len": len(public_text)},
        )
        # #endregion

    def cleanup(self) -> None:
        self._buffers.clear()
