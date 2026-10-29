import json
from pathlib import Path

from meta_sam_parser import CompletedOutcome, decode_mask_to_raster, video_segmentation_format
from PIL import Image


def save_masks(text: str, directory: Path, width: int, height: int, fps: int) -> dict:
    parser = video_segmentation_format().create_parser()
    parser.push(text)
    result = parser.finish(CompletedOutcome()).result
    if result.diagnostics:
        raise ValueError("SAM output contains malformed geometry; tracking was not accepted.")
    subjects = set()
    frames = set()
    directory.mkdir(parents=True, exist_ok=True)
    for record in result.records:
        if record.kind != "mask":
            continue
        subject, frame = record.object_id, record.frame.frame_index if record.frame else 0
        if not subject.isdigit() or len(subject) > 8 or not 0 <= frame < 600:
            raise ValueError("SAM returned invalid frame or subject identity.")
        mask = record.mask
        if mask.width * mask.height > width * height * 4:
            raise ValueError("SAM mask dimensions exceed media bounds.")
        raster = decode_mask_to_raster(mask)
        local = Image.frombytes("L", (mask.width, mask.height), raster).point(lambda p: p * 255)
        bounds = tuple(round(getattr(record.bounds, k)) for k in ("left", "top", "right", "bottom"))
        x1, y1, x2, y2 = bounds
        if not 0 <= x1 < x2 <= width or not 0 <= y1 < y2 <= height:
            raise ValueError("SAM returned an out-of-bounds mask.")
        canvas = Image.new("L", (width, height))
        canvas.paste(local.resize((x2 - x1, y2 - y1)), (x1, y1))
        target = directory / subject
        target.mkdir(exist_ok=True)
        canvas.save(target / f"{frame:06d}.png")
        subjects.add(subject)
        frames.add(frame)
    if not subjects:
        raise ValueError("No subjects matched. Try a more specific subject description.")
    manifest = {
        "fps": fps,
        "width": width,
        "height": height,
        "subjects": sorted(subjects),
        "frame_count": len(frames),
        "provider": "Meta SAM",
    }
    (directory / "manifest.json").write_text(json.dumps(manifest))
    return manifest
