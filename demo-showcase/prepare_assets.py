"""Prepare the local showcase from verified ReelOS artifacts; no paid model calls."""

import hashlib
import json
import subprocess
from pathlib import Path

import httpx
from PIL import Image

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parent
ASSETS = PROJECT / "assets"
ASSETS.mkdir(exist_ok=True)
ledger = []


def cut(name, source, start, duration):
    target = ASSETS / name
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-ss",
            str(start),
            "-i",
            str(source),
            "-t",
            str(duration),
            "-vf",
            "scale=540:960",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(target),
        ],
        check=True,
    )
    ledger.append(
        {
            "asset": name,
            "source": str(source.relative_to(ROOT)),
            "source_in": start,
            "duration": duration,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        }
    )


full = ROOT / "data/reelos-full-video-1080p.mp4"
raw = ROOT / "testing_videos/VID_20261012_002734_182_bsl.mp4"
for name, source, start, duration in [
    ("raw.mp4", raw, 0, 8),
    ("edited.mp4", full, 0, 8),
    ("glasses.mp4", full, 12, 3),
    ("classroom.mp4", full, 36, 3),
    ("label.mp4", full, 18, 5),
    ("late.mp4", full, 132, 8),
    ("loft.mp4", ROOT / "data/evaluation-media/loft-export.mp4", 1, 4),
    ("occlusion.mp4", ROOT / "data/evaluation-media/home-export.mp4", 5, 4),
]:
    cut(name, source, start, duration)
with httpx.Client(timeout=180) as client:
    base = "http://127.0.0.1:3000/api/projects/5988d17cb3a34cf2967a0b442c6d6936"
    for kind, vid in [
        ("before", "5916fdeb69cc4e829955f91a95080d96"),
        ("after", "2677c275e4b34e62a643ba692006a200"),
    ]:
        result = client.get(base + "/versions/" + vid + "/preview")
        result.raise_for_status()
        target = ASSETS / f"{kind}.mp4"
        target.write_bytes(result.content)
        ledger.append(
            {
                "asset": target.name,
                "source": base + "/versions/" + vid + "/preview",
                "sha256": hashlib.sha256(result.content).hexdigest(),
                "meaning": "Actual generated preview; opener y=0.10"
                if kind == "before"
                else "Actual revised preview; opener y=0.12",
            }
        )
    thumb = client.get(
        "http://127.0.0.1:3000/api/projects/25ec54f2c76e4b87b9357927edf8d6a9/jobs/764a526bf6e84eab9b7bc6af30dc6d66/subjects/0/thumbnail"
    )
    thumb.raise_for_status()
    (ASSETS / "sam-subject.png").write_bytes(thumb.content)
for name in ["before", "after"]:
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(ASSETS / f"{name}.mp4"),
            "-t",
            "5",
            "-vf",
            "crop=360:120:0:0",
            "-an",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            str(ASSETS / f"{name}-headline.mp4"),
        ],
        check=True,
    )
    ledger.append(
        {
            "asset": f"{name}-headline.mp4",
            "source": f"{name}.mp4",
            "crop": "360:120:0:0",
            "duration": 5,
        }
    )
for source, target, bounds in [
    ("assets-panel.png", "assets-detail.png", (24, 454, 366, 808)),
    ("history-baseline.png", "history-baseline-detail.png", (12, 675, 378, 824)),
    ("history-revision.png", "history-revision-detail.png", (12, 675, 378, 824)),
]:
    if not (ASSETS / source).exists():
        raise SystemExit(f"Capture the actual UI first: assets/{source}. See README.md.")
    Image.open(ASSETS / source).crop(bounds).save(ASSETS / target)
    ledger.append({"asset": target, "source": source, "crop_xyxy": bounds})
known = {entry["asset"] for entry in ledger}
for asset in sorted(ASSETS.iterdir()):
    if asset.suffix not in {".mp4", ".png", ".wav"}:
        continue
    if asset.name not in known:
        ledger.append(
            {
                "asset": asset.name,
                "source": "compose_audio.py: original deterministic score"
                if asset.name == "original-bed.wav"
                else "Actual ReelOS UI capture or SAM thumbnail; see README.md",
            }
        )
for entry in ledger:
    entry["sha256"] = hashlib.sha256((ASSETS / entry["asset"]).read_bytes()).hexdigest()
(PROJECT / "ASSET_LEDGER.json").write_text(json.dumps(ledger, indent=2))
print(
    "Prepared", len(ledger), "verified/local assets. UI captures are obtained separately via CUA."
)
