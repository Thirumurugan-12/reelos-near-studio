import io
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter


def subject_thumbnail(source: Path, directory: Path, subject: str) -> bytes:
    """A real source frame, cropped around and highlighting one detected SAM track."""
    manifest = json.loads((directory / "manifest.json").read_text())
    if subject not in manifest["subjects"] or not subject.isdecimal():
        raise ValueError("Choose a detected subject.")
    best, area = None, 0
    for path in sorted((directory / subject).glob("*.png")):
        with Image.open(path) as mask:
            bounds = mask.getbbox()
            size = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1]) if bounds else 0
            if size > area:
                best, area = path, size
    if best is None:
        raise ValueError("This subject has no visible tracking frames.")
    seconds = int(best.stem) / manifest["fps"]
    result = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            str(seconds),
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-f",
            "image2pipe",
            "-vcodec",
            "png",
            "-",
        ],
        capture_output=True,
        check=True,
        timeout=20,
    )
    with Image.open(io.BytesIO(result.stdout)) as decoded, Image.open(best) as stored:
        frame = decoded.convert("RGB")
        mask = stored.convert("L").resize(frame.size)
    bounds = mask.getbbox()
    highlighted = Image.composite(frame, ImageEnhance.Brightness(frame).enhance(0.3), mask)
    outline = ImageChops.subtract(mask.filter(ImageFilter.MaxFilter(5)), mask)
    highlighted.paste((178, 235, 167), (0, 0), outline)
    x1, y1, x2, y2 = bounds
    side = max(x2 - x1, y2 - y1) * 1.35
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    crop = highlighted.crop(
        tuple(round(v) for v in (cx - side / 2, cy - side / 2, cx + side / 2, cy + side / 2))
    )
    output = io.BytesIO()
    crop.resize((192, 192), Image.Resampling.LANCZOS).save(output, format="PNG")
    return output.getvalue()


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
                ["node", "--max-old-space-size=1024", str(helper), str(request), str(root)],
                capture_output=True,
                timeout=300,
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
