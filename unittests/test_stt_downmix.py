"""Tests for Discord stereo PCM downmix heuristics."""

from __future__ import annotations

import array
import audioop

from apps.bot.stt import _antiphase_fraction, _downmix_variants, _stereo_to_mono


def _interleave_stereo(left: array.array, right: array.array) -> bytes:
    out = array.array("h")
    for l_sample, r_sample in zip(left, right, strict=True):
        out.append(l_sample)
        out.append(r_sample)
    return out.tobytes()


def test_antiphase_uses_side_not_cancelled_mid() -> None:
    """When L ≈ -R, averaging cancels speech; downmix must keep energy."""
    left = array.array("h", [10000, -8000, 6000, -4000] * 200)
    right = array.array("h", [-x for x in left])
    stereo = _interleave_stereo(left, right)
    assert _antiphase_fraction(stereo) >= 0.35
    modes = [name for _, name in _downmix_variants(stereo)]
    assert modes[0] == "side"
    mono, mode = _stereo_to_mono(stereo)
    assert audioop.rms(mono, 2) > 1000
    assert mode == "side"


def test_inphase_uses_mid() -> None:
    """When L ≈ R, mid (sum) preserves speech."""
    left = array.array("h", [5000, -3000, 2000, -1000] * 200)
    right = array.array("h", left)
    stereo = _interleave_stereo(left, right)
    mono, mode = _stereo_to_mono(stereo)
    assert audioop.rms(mono, 2) > 1000
    assert mode in {"mid", "L", "R"}
