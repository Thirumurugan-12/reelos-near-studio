"""An original, deterministic 75-second instrumental bed; no samples or model calls."""

import wave
from pathlib import Path

import numpy as np

sr, duration = 48000, 75
mix = np.zeros((sr * duration, 2), dtype=np.float64)
chords = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
rng = np.random.default_rng(20261030)


def note(start, midi, length, gain, pan):
    i = round(start * sr)
    n = min(round(length * sr), len(mix) - i)
    if n <= 0:
        return
    t = np.arange(n) / sr
    f = 440 * 2 ** ((midi - 69) / 12)
    env = (1 - np.exp(-t * 40)) * np.exp(-t * 2.4) * np.minimum(1, (length - t) * 12)
    signal = (
        np.sin(2 * np.pi * f * t + 0.45 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 5))
        * env
        * gain
    )
    mix[i : i + n, 0] += signal * np.sqrt((1 - pan) / 2)
    mix[i : i + n, 1] += signal * np.sqrt((1 + pan) / 2)


# Original voicing and note pattern, with quiet filtered percussive ticks.
for beat in range(125):
    start = beat * 0.6
    chord = chords[(beat // 8) % 4]
    if beat % 8 == 0:
        for j, midi in enumerate(chord):
            note(start, midi, 4.0, 0.10, (-0.3, 0, 0.3)[j])
    if beat % 2 == 0:
        note(start + 0.06, chord[(beat // 2) % 3] + 12, 1.15, 0.11, (-0.2, 0.2)[(beat // 2) % 2])
    i = round(start * sr)
    n = min(960, len(mix) - i)
    if n > 0:
        noise = rng.normal(0, 0.012, n) * np.exp(-np.arange(n) / (sr * 0.006))
        mix[i : i + n] += noise[:, None]
fade = np.minimum(1, np.arange(len(mix)) / (sr * 0.5)) * np.minimum(
    1, (len(mix) - 1 - np.arange(len(mix))) / (sr * 3)
)
mix *= fade[:, None]
mix *= 0.8 / max(np.max(np.abs(mix)), 1e-6)
path = Path(__file__).parent / "assets/original-bed.wav"
with wave.open(str(path), "wb") as f:
    f.setnchannels(2)
    f.setsampwidth(2)
    f.setframerate(sr)
    f.writeframes((mix * 32767).astype("<i2").tobytes())
print(path)
