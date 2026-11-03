"""Original, deterministic instrumental beds for multi-clip reels; no samples, downloads or
model calls.

- morning: ported unchanged from demo-showcase/compose_audio.py. 100 BPM (0.6 s beats),
  Am–F–C–G, one chord every eight beats (4.8 s). Calm and Clean reels cut on this grid.
- drive: 120 BPM (0.5 s beats), same progression one chord per bar (2 s), with kick, clap,
  hats, bass and short chord stabs. Energetic reels cut on this grid.
"""

import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 48000
DURATION = 75
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
BEATS = {"morning": 0.6, "drive": 0.5}


class _Mix:
    def __init__(self):
        self.data = np.zeros((SAMPLE_RATE * DURATION, 2), dtype=np.float64)

    def add(self, start: float, signal: np.ndarray, pan: float | None = 0.0):
        i = round(start * SAMPLE_RATE)
        n = min(len(signal), len(self.data) - i)
        if n <= 0:
            return
        if pan is None:  # unpanned: full level in both channels
            self.data[i : i + n] += signal[:n, None]
            return
        self.data[i : i + n, 0] += signal[:n] * np.sqrt((1 - pan) / 2)
        self.data[i : i + n, 1] += signal[:n] * np.sqrt((1 + pan) / 2)

    def note(self, start, midi, length, gain, pan):
        n = round(length * SAMPLE_RATE)
        t = np.arange(n) / SAMPLE_RATE
        f = 440 * 2 ** ((midi - 69) / 12)
        env = (1 - np.exp(-t * 40)) * np.exp(-t * 2.4) * np.minimum(1, (length - t) * 12)
        tone = np.sin(2 * np.pi * f * t + 0.45 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 5))
        self.add(start, tone * env * gain, pan)

    def finish(self, fade_in: float, fade_out: float, peak: float) -> np.ndarray:
        n = len(self.data)
        fade = np.minimum(1, np.arange(n) / (SAMPLE_RATE * fade_in)) * np.minimum(
            1, (n - 1 - np.arange(n)) / (SAMPLE_RATE * fade_out)
        )
        self.data *= fade[:, None]
        self.data *= peak / max(np.max(np.abs(self.data)), 1e-6)
        return self.data


def _morning() -> np.ndarray:
    mix, rng = _Mix(), np.random.default_rng(20261030)
    for beat in range(125):
        start = beat * 0.6
        chord = CHORDS[(beat // 8) % 4]
        if beat % 8 == 0:
            for j, midi in enumerate(chord):
                mix.note(start, midi, 4.0, 0.10, (-0.3, 0, 0.3)[j])
        if beat % 2 == 0:
            pan = (-0.2, 0.2)[(beat // 2) % 2]
            mix.note(start + 0.06, chord[(beat // 2) % 3] + 12, 1.15, 0.11, pan)
        noise = rng.normal(0, 0.012, 960) * np.exp(-np.arange(960) / (SAMPLE_RATE * 0.006))
        mix.add(start, noise, None)
    return mix.finish(0.5, 3, 0.8)


def _drive() -> np.ndarray:
    mix, rng = _Mix(), np.random.default_rng(20261103)
    sr = SAMPLE_RATE
    kick_t = np.arange(round(0.32 * sr)) / sr
    sweep = 45 + 75 * np.exp(-kick_t * 28)
    kick = np.sin(2 * np.pi * np.cumsum(sweep) / sr) * np.exp(-kick_t * 11) * 0.55
    clap_n = round(0.16 * sr)
    for beat in range(150):
        start = beat * 0.5
        chord = CHORDS[(beat // 4) % 4]
        mix.add(start, kick)
        if beat % 2 == 1:
            clap = rng.normal(0, 1, clap_n) * np.exp(-np.arange(clap_n) / (sr * 0.035)) * 0.10
            mix.add(start, clap, 0.1)
        hat = np.diff(rng.normal(0, 1, 1201)) * np.exp(-np.arange(1200) / (sr * 0.004)) * 0.03
        mix.add(start + 0.25, hat, -0.25)
        mix.note(start, chord[0] - 24, 0.22, 0.20, 0)
        mix.note(start + 0.25, chord[0] - 24, 0.18, 0.12, 0)
        if beat % 2 == 0:
            for j, midi in enumerate(chord):
                mix.note(start + 0.25, midi + 12, 0.2, 0.05, (-0.35, 0, 0.35)[j])
    return mix.finish(0.2, 2, 0.85)


def bed(name: str, root: Path) -> Path:
    """Write a bed once under the data root and reuse it."""
    path = root / "music" / f"{name}-v1.wav"
    if path.exists():
        return path
    data = {"morning": _morning, "drive": _drive}[name]()
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".partial")
    with wave.open(str(partial), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes((data * 32767).astype("<i2").tobytes())
    partial.rename(path)
    return path


def morning_bed(root: Path) -> Path:
    return bed("morning", root)
