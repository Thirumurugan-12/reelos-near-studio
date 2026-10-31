"""Evaluate all recipes on authorised footage and cached real SAM masks, no paid calls."""

import argparse
import json
import time
from pathlib import Path

from PIL import ImageDraw

from reelos.catalog_contracts import LOOKS, catalog
from reelos.catalog_renderer import prepare_catalog, source_frame
from reelos.catalog_samples import sample_params
from reelos.media import MaskTrack, frame_subject, render
from reelos.timeline import EditPlan

p = argparse.ArgumentParser()
p.add_argument("--source", type=Path, required=True)
p.add_argument("--track", type=Path, required=True)
p.add_argument("--output", type=Path, required=True)
p.add_argument("--width", type=int, default=1080)
p.add_argument("--render", action="store_true")
args = p.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
rows = catalog() + [{"id": id, "label": id.replace("-", " ").title()} for id in LOOKS]
effects = []
for i, row in enumerate(rows):
    params = sample_params(row["id"])
    start = round(i * 3.45 + 0.2, 2)
    effects.append(
        {
            "id": f"catalog_{i + 1:02}",
            "type": "catalog_effect",
            "start": start,
            "end": round(start + 3.2, 2),
            "subject_id": "0",
            "reason": "Catalog demonstration; preview copy and numbers are illustrative.",
            "params": params.model_dump(),
        }
    )
plan = EditPlan.model_validate(
    {
        "asset_id": "6cf53766582d495ebfeeef1fe25107d4",
        "source_out": 167.9004,
        "output_mode": "full",
        "framing": {"scale": 0.78, "offset_y": 0.2},
        "effects": effects,
    }
)
(args.output / "plan.json").write_text(json.dumps(plan.model_dump(), indent=2))
track = MaskTrack(args.track)
if args.render:
    started = time.monotonic()
    render(
        args.source,
        plan,
        args.output / f"catalog-{args.width}.mp4",
        width=args.width,
        track=track,
        progress=lambda v: print(f"{v:.1%}", flush=True),
    )
    print("Render seconds", time.monotonic() - started, flush=True)
else:
    prepared = prepare_catalog(plan, args.source, None, args.width, track)
    reports = []
    for i, e in enumerate(plan.effects):
        started = time.monotonic()
        for offset in [0.2, 1.5, 2.9]:
            t = e.start + offset
            frame = source_frame(args.source, t, (args.width, args.width * 16 // 9))
            frame, masks = frame_subject(frame, track.at(t, frame.size), plan.framing)
            prepared.states = {}
            rendered = prepared.apply(frame, t, masks)
            rendered.thumbnail((360, 640))
            ImageDraw.Draw(rendered).text(
                (8, 8), rows[i]["label"], fill="white", stroke_width=2, stroke_fill="black"
            )
            rendered.save(args.output / f"{i + 1:02}-{offset}.webp")
        reports.append(
            {
                "fx": rows[i]["id"],
                "native_width": args.width,
                "sample_times": [e.start + v for v in [0.2, 1.5, 2.9]],
                "status": "rendered",
                "seconds": time.monotonic() - started,
            }
        )
        (args.output / "verification.json").write_text(json.dumps(reports, indent=2))
        print(rows[i]["id"], "rendered", flush=True)
