"""Local Piper TTS via the piper CLI and ONNX voice models."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Mapping

from apps.bot.tts import TtsSynthesisError

LOGGER = logging.getLogger("ttstt-bot.piper")

# Fallback when PIPER_DEFAULT_VOICE is unset (e.g. unit tests).
DEFAULT_PIPER_VOICE = "en_US-lessac-medium"
MIN_LENGTH_SCALE = 0.25


MAX_LENGTH_SCALE = 4.0


def get_default_piper_voice() -> str:
    """Piper voice basename from PIPER_DEFAULT_VOICE, else DEFAULT_PIPER_VOICE."""
    configured = os.getenv("PIPER_DEFAULT_VOICE", "").strip()
    return configured or DEFAULT_PIPER_VOICE


def list_piper_voices(model_dir: str | Path) -> tuple[str, ...]:
    """Voice basenames from ``*.onnx`` files in ``model_dir`` (for slash-command autocomplete)."""

    root = Path(model_dir)
    if not root.is_dir():
        return ()

    discovered = sorted({path.stem for path in root.glob("*.onnx")})
    if not discovered:
        return ()

    default_voice = get_default_piper_voice()
    ordered: list[str] = []
    seen: set[str] = set()
    if default_voice in discovered:
        ordered.append(default_voice)
        seen.add(default_voice)
    for name in discovered:
        if name not in seen:
            ordered.append(name)
            seen.add(name)
    return tuple(ordered)


def speed_to_length_scale(speed: float) -> float:
    """Map user speed (0.5–2.0, 1.0 = normal) to Piper length_scale (lower = faster)."""
    clamped = max(0.5, min(2.0, speed))
    scale = 1.0 / clamped
    return max(MIN_LENGTH_SCALE, min(MAX_LENGTH_SCALE, scale))


def pitch_to_playback_factor(pitch: float) -> float:
    """Map user pitch (-20..20) to a playback rate multiplier (12-TET semitones)."""
    return 2.0 ** (pitch / 12.0)


def read_wav_sample_rate(wav_bytes: bytes, *, default: int = 22050) -> int:
    """Return sample rate from a PCM WAV header; Piper commonly uses 22050 Hz."""
    if len(wav_bytes) < 28 or wav_bytes[0:4] != b"RIFF" or wav_bytes[8:12] != b"WAVE":
        return default
    rate = int.from_bytes(wav_bytes[24:28], "little")
    return rate if rate > 0 else default


def resolve_piper_model_path(model_dir: Path, voice: str) -> Path:
    name = voice.strip()
    if not name:
        raise TtsSynthesisError("Piper voice must be non-empty")
    if name.endswith(".onnx"):
        path = model_dir / name
    else:
        path = model_dir / f"{name}.onnx"
    if not path.is_file():
        raise TtsSynthesisError(
            f"Piper model not found: {path}. Install voices under PIPER_MODEL_DIR."
        )
    json_path = path.with_suffix(".onnx.json")
    if not json_path.is_file():
        alt_json = path.parent / f"{path.stem}.json"
        if not alt_json.is_file():
            LOGGER.warning("Piper model config JSON not found beside %s", path)
    return path


class PiperTtsClient:
    """Synthesize speech using the piper binary and local ONNX models."""

    def __init__(
        self,
        *,
        model_dir: str | Path,
        executable: str = "piper",
        default_voice: str | None = None,
        ffmpeg_executable: str | None = None,
        synthesis_timeout_sec: float = 60.0,
    ) -> None:
        self._model_dir = Path(model_dir)
        if not self._model_dir.is_dir():
            raise ValueError(f"PIPER_MODEL_DIR is not a directory: {self._model_dir}")
        resolved_exe = shutil.which(executable) or executable
        self._executable = resolved_exe
        self._default_voice = default_voice if default_voice is not None else get_default_piper_voice()
        self._ffmpeg_executable = ffmpeg_executable
        self._timeout = synthesis_timeout_sec
        self._installed_voices = list_piper_voices(self._model_dir)

    @property
    def installed_voices(self) -> tuple[str, ...]:
        return self._installed_voices

    def synthesize(self, text: str, voice_prefs: Mapping[str, object]) -> bytes:
        normalized = text.strip()
        if not normalized:
            raise TtsSynthesisError("text must not be empty")

        voice = str(voice_prefs.get("voice") or self._default_voice)
        speed = float(voice_prefs.get("speed") or 1.0)
        pitch = float(voice_prefs.get("pitch") or 0.0)
        length_scale = speed_to_length_scale(speed)

        model_path = resolve_piper_model_path(self._model_dir, voice)
        wav_bytes = self._run_piper(
            text=normalized,
            model_path=model_path,
            length_scale=length_scale,
        )
        if pitch != 0.0 and self._ffmpeg_executable:
            wav_bytes = self._apply_pitch_shift(wav_bytes, pitch=pitch)
        return wav_bytes

    def _run_piper(self, *, text: str, model_path: Path, length_scale: float) -> bytes:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name

        try:
            cmd = [
                self._executable,
                "--model",
                str(model_path),
                "--output_file",
                output_path,
                "--length_scale",
                str(length_scale),
            ]
            proc = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=self._timeout,
                check=False,
            )
            if proc.returncode != 0:
                stderr = proc.stderr.decode("utf-8", errors="replace").strip()
                raise TtsSynthesisError(
                    f"Piper failed (exit {proc.returncode}): {stderr or 'no stderr'}"
                )
            out = Path(output_path)
            if not out.is_file() or out.stat().st_size < 44:
                raise TtsSynthesisError("Piper did not produce a valid WAV file")
            return out.read_bytes()
        except FileNotFoundError as exc:
            raise TtsSynthesisError(
                f"Piper executable not found: {self._executable}. "
                "Install piper and set PIPER_EXECUTABLE, or use /tts_provider_set deepgram."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise TtsSynthesisError("Piper synthesis timed out") from exc
        finally:
            try:
                os.unlink(output_path)
            except OSError:
                pass

    def _apply_pitch_shift(self, wav_bytes: bytes, *, pitch: float) -> bytes:
        """Shift pitch with ffmpeg; pitch is in semitone-like units (-20..20)."""
        sample_rate = read_wav_sample_rate(wav_bytes)
        factor = pitch_to_playback_factor(pitch)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as inp:
            inp_path = inp.name
            inp.write(wav_bytes)
        out_path = inp_path + ".pitched.wav"
        try:
            cmd = [
                self._ffmpeg_executable or "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                inp_path,
                "-af",
                f"asetrate={sample_rate}*{factor:.6f},aresample={sample_rate}",
                out_path,
            ]
            proc = subprocess.run(cmd, capture_output=True, timeout=30, check=False)
            if proc.returncode != 0:
                LOGGER.warning("ffmpeg pitch shift failed; using unmodified Piper audio")
                return wav_bytes
            return Path(out_path).read_bytes()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            LOGGER.warning("ffmpeg pitch shift unavailable; using unmodified Piper audio")
            return wav_bytes
        finally:
            for path in (inp_path, out_path):
                try:
                    os.unlink(path)
                except OSError:
                    pass
