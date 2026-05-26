from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from apps.bot.piper_tts import (
    DEFAULT_PIPER_VOICE,
    PiperTtsClient,
    get_default_piper_voice,
    list_piper_voices,
    resolve_piper_model_path,
    speed_to_length_scale,
)
from apps.bot.tts import TtsSynthesisError


def test_get_default_piper_voice_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIPER_DEFAULT_VOICE", "en_US-libritts_r-medium")
    assert get_default_piper_voice() == "en_US-libritts_r-medium"


def test_get_default_piper_voice_falls_back_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PIPER_DEFAULT_VOICE", raising=False)
    assert get_default_piper_voice() == DEFAULT_PIPER_VOICE


def test_speed_to_length_scale_faster_speech_has_lower_scale() -> None:
    assert speed_to_length_scale(2.0) < speed_to_length_scale(1.0)
    assert speed_to_length_scale(0.5) > speed_to_length_scale(1.0)


def test_list_piper_voices_scans_onnx_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PIPER_DEFAULT_VOICE", "en_US-libritts_r-medium")
    (tmp_path / "en_US-libritts_r-medium.onnx").write_bytes(b"\x00" * 64)
    (tmp_path / "en_US-lessac-medium.onnx").write_bytes(b"\x00" * 64)

    voices = list_piper_voices(tmp_path)

    assert voices == ("en_US-libritts_r-medium", "en_US-lessac-medium")


def test_resolve_piper_model_path_appends_onnx(tmp_path: Path) -> None:
    model = tmp_path / "en_US-lessac-medium.onnx"
    model.write_bytes(b"\x00" * 64)

    resolved = resolve_piper_model_path(tmp_path, "en_US-lessac-medium")

    assert resolved == model


def test_piper_client_exposes_installed_voices(tmp_path: Path) -> None:
    (tmp_path / "en_US-libritts_r-medium.onnx").write_bytes(b"\x00" * 64)
    client = PiperTtsClient(model_dir=tmp_path, executable="/usr/bin/piper", ffmpeg_executable=None)
    assert "en_US-libritts_r-medium" in client.installed_voices


def test_piper_synthesize_invokes_cli(tmp_path: Path) -> None:
    model = tmp_path / "en_US-lessac-medium.onnx"
    model.write_bytes(b"\x00" * 64)
    fake_wav = b"RIFF" + b"\x00" * 40 + b"WAVE"

    def fake_run(cmd, **kwargs):
        out_idx = cmd.index("--output_file") + 1
        Path(cmd[out_idx]).write_bytes(fake_wav)
        return subprocess.CompletedProcess(cmd, 0, b"", b"")

    client = PiperTtsClient(model_dir=tmp_path, executable="/usr/bin/piper", ffmpeg_executable=None)

    with patch("apps.bot.piper_tts.subprocess.run", side_effect=fake_run):
        audio = client.synthesize("hello", {"voice": "en_US-lessac-medium", "speed": 1.0, "pitch": 0.0})

    assert audio == fake_wav


def test_piper_synthesize_raises_when_model_missing(tmp_path: Path) -> None:
    client = PiperTtsClient(model_dir=tmp_path, executable="/usr/bin/piper")

    with pytest.raises(TtsSynthesisError, match="not found"):
        client.synthesize("hello", {"voice": "missing-voice"})


def test_piper_synthesize_raises_when_binary_missing(tmp_path: Path) -> None:
    model = tmp_path / "en_US-lessac-medium.onnx"
    model.write_bytes(b"\x00" * 64)
    client = PiperTtsClient(model_dir=tmp_path, executable="/nonexistent/piper")

    with patch("apps.bot.piper_tts.subprocess.run", side_effect=FileNotFoundError):
        with pytest.raises(TtsSynthesisError, match="not found"):
            client.synthesize("hello", {"voice": "en_US-lessac-medium"})
