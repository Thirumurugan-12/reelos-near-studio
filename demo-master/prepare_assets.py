"""Derive the local master from existing evidence; no model calls or credential access."""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
ASSETS.mkdir(exist_ok=True)
ledger = []


def copy(name, source, meaning):
    shutil.copyfile(ROOT / source, ASSETS / name)
    ledger.append({"asset": name, "source": source, "meaning": meaning})


def cut(name, source, start, duration, audio=True):
    args = [
        "ffmpeg",
        "-v",
        "error",
        "-y",
        "-ss",
        str(start),
        "-i",
        str(ROOT / source),
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
    ]
    args += ["-c:a", "aac"] if audio else ["-an"]
    subprocess.run(args + [str(ASSETS / name)], check=True)
    ledger.append({"asset": name, "source": source, "source_in": start, "duration": duration})


# Verify/rebuild the entire gallery before updating its provenance ledger.
subprocess.run(
    [sys.executable, str(ROOT / "demo-showcase/prepare_effect_gallery.py"), "--target", str(HERE)],
    check=True,
)
gallery = json.loads((HERE / "EFFECT_GALLERY.json").read_text())


copy("raw20.mp4", "data/demo-inputs/new-raw-20s.mp4", "Authorized 20-second source derivative")
copy(
    "fresh20.mp4",
    "data/layout-followup/run-01-export.mp4",
    "Actual initial Muse plan; no manual layout repair",
)
copy(
    "fresh-camera.mp4",
    "data/layout-followup/run-02-export.mp4",
    "Actual camera initial Muse plan; silent technical footage",
)
for name in [
    "canvas-workspace.png",
    "canvas-media.png",
    "canvas-history-baseline.png",
    "canvas-history-revision.png",
    "sam-subject.png",
    "before.mp4",
    "after.mp4",
    "before-headline.mp4",
    "after-headline.mp4",
    "glasses.mp4",
    "classroom.mp4",
    "late.mp4",
    "loft.mp4",
    "occlusion.mp4",
    "original-bed.wav",
]:
    copy(
        name,
        "demo-showcase/assets/" + name,
        "Existing real evidence; see demo-showcase/ASSET_LEDGER.json",
    )
copy(
    "recovery-workspace.png",
    "data/title-layout-recovery/desktop.png",
    "Actual Canvas Pro recovery controls and recovered main preview",
)
copy(
    "fresh-workspace.png",
    "data/layout-followup/workspace.png",
    "Actual fresh Muse layout in Canvas Pro",
)
cut("catalog.mp4", "data/catalog-evaluation/full-render/catalog-1080.mp4", 10.4, 30, False)
subprocess.run(
    [
        "ffmpeg",
        "-v",
        "error",
        "-y",
        "-i",
        str(ASSETS / "original-bed.wav"),
        "-t",
        "47.4",
        "-af",
        "afade=t=out:st=44.4:d=3",
        str(ASSETS / "bed-tail.wav"),
    ],
    check=True,
)
ledger.append(
    {
        "asset": "bed-tail.wav",
        "source": "original-bed.wav",
        "meaning": "First 47.4s with final 3s fade; no new music synthesis",
    }
)
ledger.extend(
    {
        "asset": "effect-gallery/" + row["asset"],
        "source": "EFFECT_GALLERY.json",
        "source_in": row["source_in"],
        "source_out": row["source_out"],
        "meaning": row["name"],
    }
    for row in gallery["tiles"]
)
for item in ledger:
    item["sha256"] = hashlib.sha256((ASSETS / item["asset"]).read_bytes()).hexdigest()
(HERE / "ASSET_LEDGER.json").write_text(json.dumps(ledger, indent=2) + "\n")
print("Prepared", len(ledger), "existing/local assets")
