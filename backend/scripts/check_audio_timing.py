"""Read-only source/output audio alignment checks; no provider access or app writes."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np


def window_delay(source, output, rate, start, duration, source_in=0, max_lag=0.5):
    """Normalized cross-correlation; positive lag means exported audio is later."""
    n = round(duration * rate)
    lag = round(max_lag * rate)
    first = round((source_in + start) * rate)
    left = round(start * rate) - lag
    if n < 2 or lag < 1 or first < 0 or left < 0:
        raise ValueError("Comparison window is outside the decoded audio.")
    a = np.asarray(source[first : first + n], dtype=np.float64)
    b = np.asarray(output[left : left + n + 2 * lag], dtype=np.float64)
    if len(a) != n or len(b) != n + 2 * lag:
        raise ValueError("Comparison window is outside the decoded audio.")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Audio contains non-finite samples.")
    a = a - a.mean()
    energy_a = np.dot(a, a)
    if energy_a < 1e-12:
        raise ValueError("Source window is silence; alignment is inconclusive.")
    fft_size = 1 << (len(a) + len(b) - 2).bit_length()
    numerator = np.fft.irfft(
        np.fft.rfft(b, fft_size) * np.conj(np.fft.rfft(a, fft_size)), fft_size
    )[: 2 * lag + 1]
    sums = np.concatenate(([0], np.cumsum(b)))
    squares = np.concatenate(([0], np.cumsum(b * b)))
    energy_b = np.maximum(0, squares[n:] - squares[:-n] - (sums[n:] - sums[:-n]) ** 2 / n)
    valid = energy_b > 1e-12
    if not valid.any():
        raise ValueError("Output window is silence; alignment is inconclusive.")
    scores = np.zeros_like(numerator)
    scores[valid] = numerator[valid] / np.sqrt(energy_a * energy_b[valid])
    peak = int(np.argmax(np.abs(scores)))
    return {
        "output_start": start,
        "source_start": source_in + start,
        "window_seconds": duration,
        "lag_ms": (peak - lag) / rate * 1000,
        "correlation": float(np.clip(scores[peak], -1, 1)),
        "search_boundary": peak in (0, 2 * lag),
    }


def decode(path, rate):
    result = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-ac",
            "1",
            "-ar",
            str(rate),
            "-f",
            "f32le",
            "-",
        ],
        capture_output=True,
        check=True,
        timeout=180,
    )
    return np.frombuffer(result.stdout, dtype="<f4")


def stream_starts(path):
    metadata = json.loads(
        subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=codec_type,start_time",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            check=True,
            timeout=30,
        ).stdout
    )
    starts = {}
    for stream in metadata["streams"]:
        if stream["codec_type"] in ("audio", "video"):
            starts.setdefault(stream["codec_type"], float(stream["start_time"]))
    if set(starts) != {"audio", "video"} or abs(starts["audio"] - starts["video"]) > 1e-6:
        raise ValueError("This checker requires matching audio/video stream start timestamps.")
    return starts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--at", type=float, nargs="+", required=True)
    parser.add_argument("--window", type=float, default=5)
    parser.add_argument("--source-in", type=float, default=0)
    args = parser.parse_args()
    rate = 24000
    starts = {"source": stream_starts(args.source), "output": stream_starts(args.output)}
    source, output = decode(args.source, rate), decode(args.output, rate)
    samples = [window_delay(source, output, rate, t, args.window, args.source_in) for t in args.at]
    for sample in samples:
        sample["pass"] = (
            not sample["search_boundary"]
            and abs(sample["lag_ms"]) <= 100
            and abs(sample["correlation"]) >= 0.9
        )
    print(
        json.dumps(
            {
                "sample_rate": rate,
                "max_search_lag_ms": 500,
                "stream_starts": starts,
                "source": str(args.source),
                "output": str(args.output),
                "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
                "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
                "samples": samples,
                "pass": all(sample["pass"] for sample in samples),
                "scope": (
                    "Decoded audio alignment only; not human listening or visual lip-sync review."
                ),
            },
            indent=2,
        )
    )
    return 0 if all(sample["pass"] for sample in samples) else 1


if __name__ == "__main__":
    raise SystemExit(main())
