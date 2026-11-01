"""Rebuild private gallery clips from the verified full sampler; no model requests.

The editable HTML and frozen interval manifest are intentionally not regenerated.
"""

import argparse
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--target", type=Path, default=Path(__file__).resolve().parent)
parser.add_argument(
    "--source", type=Path, default=ROOT / "data/catalog-evaluation/full-render/catalog-1080.mp4"
)
args = parser.parse_args()
target = args.target.resolve()
manifest = json.loads((target / "EFFECT_GALLERY.json").read_text())
if hashlib.sha256(args.source.read_bytes()).hexdigest() != manifest["render_sha256"]:
    raise SystemExit(
        "Source is not the verified sampler. Inspect its provenance before rebuilding."
    )
clips = target / "assets/effect-gallery"
clips.mkdir(parents=True, exist_ok=True)


def build(row):
    output = clips / row["asset"]
    if not output.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-ss",
                str(row["source_in"]),
                "-i",
                str(args.source),
                "-vf",
                "scale=432:768,setsar=1,fps=30,setpts=PTS-STARTPTS",
                "-frames:v",
                "96",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(output),
            ],
            check=True,
        )
    metadata = json.loads(
        subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=nb_frames,width,height",
                "-of",
                "json",
                str(output),
            ],
            capture_output=True,
            check=True,
        ).stdout
    )["streams"][0]
    if metadata != {"width": 432, "height": 768, "nb_frames": "96"}:
        raise SystemExit(f"Invalid gallery clip: {output.name}")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    if digest != row["sha256"]:
        raise SystemExit(
            f"Gallery clip identity mismatch: {output.name}. "
            "The file was preserved. Verify the footage and encoder version before replacing it "
            "or reviewing a new manifest."
        )
    return {"asset": row["asset"], "sha256": digest}


with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(build, manifest["tiles"]))
print(json.dumps({"verified_clips": len(results), "clips": results}, indent=2))
