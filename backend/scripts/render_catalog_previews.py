"""Build public, explicitly illustrated previews with the actual catalog renderer."""

import argparse
import json
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import ImageDraw

from reelos.catalog_contracts import LOOKS, catalog
from reelos.catalog_renderer import CatalogRenderer
from reelos.catalog_samples import illustrated_cards, illustrated_source, sample_params
from reelos.timeline import EditPlan

p = argparse.ArgumentParser()
p.add_argument("--output", type=Path)
p.add_argument("--width", type=int, default=360)
p.add_argument("--stills", action="store_true")
p.add_argument("--force", action="store_true", help="Regenerate existing previews atomically")
args = p.parse_args()
root = args.output or Path(__file__).resolve().parents[1] / "reelos/catalog_previews"
root.mkdir(parents=True, exist_ok=True)
size = (args.width, args.width * 16 // 9)
image, mask = illustrated_source(size)
cards = illustrated_cards()
results = []
for name in [r["id"] for r in catalog()] + list(LOOKS):
    start = time.monotonic()
    params = sample_params(name)
    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 3,
            "effects": [
                {
                    "id": "sample",
                    "type": "catalog_effect",
                    "subject_id": "0",
                    "start": 0,
                    "end": 3,
                    "params": params.model_dump(),
                }
            ],
        }
    )
    anchor = (size[0] * 0.5, size[1] * 0.31, size[0] * 0.30)
    renderer = CatalogRenderer(
        plan, cards={"sample": cards}, starts={"sample": (image, mask, anchor)}
    )
    renderer.detector = None
    if args.stills:
        for t in [0.2, 1.5, 2.7]:
            # Independent preparation catches hidden dependence on earlier render calls.
            renderer.states = {}
            frame = renderer.apply(image.copy(), t, {"0": mask})
            frame.thumbnail((360, 640))
            frame.save(root / f"{name}-{t}.webp")
    else:
        target = root / (name + ".mp4")
        part = root / (name + ".tmp.mp4")
        if target.exists() and not args.force:
            print(name, "already rendered", flush=True)
            continue
        encoder = subprocess.Popen(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-s",
                f"{size[0]}x{size[1]}",
                "-r",
                "30",
                "-i",
                "pipe:0",
                "-an",
                "-c:v",
                "libx264",
                "-crf",
                "24",
                "-preset",
                "veryfast",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(part),
            ],
            stdin=subprocess.PIPE,
        )
        try:
            for index in range(90):
                frame = renderer.apply(image.copy(), index / 30, {"0": mask})
                d = ImageDraw.Draw(frame)
                d.rectangle((0, size[1] - 24, size[0], size[1]), fill="#102023")
                d.text((7, size[1] - 18), "ILLUSTRATED PREVIEW / EXAMPLE DATA", fill="white")
                if index == 45:
                    frame.save(root / (name + ".webp"))
                encoder.stdin.write(np.asarray(frame).tobytes())
            encoder.stdin.close()
            if encoder.wait(timeout=30):
                raise RuntimeError("Preview encoder failed")
            part.replace(target)
        finally:
            if encoder.poll() is None:
                encoder.kill()
                encoder.wait()
    row = {
        "fx": name,
        "width": args.width,
        "seconds": round(time.monotonic() - start, 3),
        "status": "rendered",
    }
    results.append(row)
    (root / "verification.json").write_text(json.dumps(results, indent=2))
    print(row, flush=True)
