import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


def save_masks(text: str, directory: Path, width: int, height: int, fps: int) -> dict:
    subjects = set()
    frames = set()
    directory.mkdir(parents=True, exist_ok=True)
    helper = Path(__file__).resolve().parents[1] / "scripts" / "decode-sam.mjs"
    with tempfile.TemporaryDirectory(dir=directory) as temp:
        root = Path(temp)
        request = root / "input.json"
        request.write_text(json.dumps({"text": text, "width": width, "height": height}))
        try:
            subprocess.run(
                ["node", "--max-old-space-size=256", str(helper), str(request), str(root)],
                capture_output=True,
                timeout=120,
                check=True,
            )
        except subprocess.SubprocessError as exc:
            raise ValueError("SAM output could not be decoded into valid tracking masks.") from exc
        records = json.loads((root / "records.json").read_text())
        for record in records:
            subject, frame = record["id"], record["frame"]
            raster = (root / record["filename"]).read_bytes()
            local = Image.frombytes("L", (record["width"], record["height"]), raster)
            local = local.point(lambda p: p * 255)
            bounds = tuple(round(record["bounds"][k]) for k in ("left", "top", "right", "bottom"))
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
