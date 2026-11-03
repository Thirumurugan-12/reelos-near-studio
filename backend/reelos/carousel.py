"""Instagram carousels from a multi-clip reel, designed with Muse Image.

Real frames from Muse's chosen shots are the references; Muse Image restyles them into 4:5
editorial images (edit mode, no added people, objects or text). ReelOS then typesets the
title, captions and slide counter itself, so every word on a slide is exactly what the
creator and Muse's plan said, never model-drawn lettering.
"""

import base64
import io
import shutil
import subprocess
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from reelos import montage

W, H = 1080, 1350
FONTS = Path(__file__).parent / "vendor" / "fonts"
MAX_SLIDES = 5  # plus the cover
MOODS = {
    "calm": "soft cinematic light, gentle mist, calm muted colour",
    "energetic": "punchy contrast, vivid saturated colour, crisp detail",
    "clean": "natural true-to-life colour, clean balanced light",
}
GUARD = (
    "Keep the real scene, objects and composition. Do not add people, animals, vehicles, "
    "text, logos or watermarks. Photorealistic, 4:5 portrait."
)


def pick_shots(shots: list[dict]) -> list[dict]:
    """Up to five shots spread across the reel, in reel order."""
    if len(shots) <= MAX_SLIDES:
        return list(shots)
    step = (len(shots) - 1) / (MAX_SLIDES - 1)
    return [shots[round(i * step)] for i in range(MAX_SLIDES)]


def frame_jpeg(clip_file: Path, seconds: float, width: int = 1024) -> bytes:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, seconds):.3f}", "-i", str(clip_file)]
        + ["-frames:v", "1", "-vf", f"scale={width}:-2", "-f", "image2", "-c:v", "mjpeg", "-"],
        capture_output=True,
        check=True,
        timeout=60,
    )
    if not result.stdout:
        raise ValueError("Could not read a frame for the carousel.")
    return result.stdout


def data_url(jpeg: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(jpeg).decode()


def prompts(style: str, count: int) -> list[str]:
    mood = MOODS.get(style, MOODS["calm"])
    cover = (
        "Design a striking Instagram carousel cover from these real photos of one outing. "
        f"Use one of the actual scenes as the hero image with {mood}. Keep the top third calm "
        f"and uncluttered for a title. {GUARD}"
    )
    slide = f"Restyle this real photo as an editorial magazine image with {mood}. {GUARD}"
    return [cover] + [slide] * count


def _font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def _cover_fit(image: Image.Image) -> Image.Image:
    scale = max(W / image.width, H / image.height)
    resized = image.convert("RGB").resize(
        (round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS
    )
    left, top = (resized.width - W) // 2, (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H))


def _shade(canvas: Image.Image, top: bool, strength: int = 190, span: float = 0.45):
    overlay = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(overlay)
    rows = int(H * span)
    for i in range(rows):
        alpha = int(strength * (1 - i / rows) ** 1.6)
        y = i if top else H - 1 - i
        draw.line([(0, y), (W, y)], fill=alpha)
    canvas.paste(Image.new("RGB", (W, H), (8, 10, 9)), mask=overlay)


def _wrap(draw, text: str, font, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + ([line] if line else [])


def compose_cover(art: bytes, title: str, dateline: str, count: int) -> Image.Image:
    canvas = _cover_fit(Image.open(io.BytesIO(art)))
    _shade(canvas, top=True, strength=200, span=0.5)
    _shade(canvas, top=False, strength=150, span=0.25)
    draw = ImageDraw.Draw(canvas)
    font = _font("ArchivoBlack-Regular.ttf", 112)
    y = 120
    for line in _wrap(draw, (title or "Reel").upper(), font, W - 160)[:3]:
        draw.text((80, y), line, font=font, fill=(244, 244, 241))
        y += 118
    if dateline:
        mono = _font("SpaceMono-Bold.ttf", 34)
        box = draw.textbbox((0, 0), dateline, font=mono)
        draw.rectangle((80, y + 24, 80 + box[2] + 36, y + 24 + box[3] + 24), fill=(234, 255, 129))
        draw.text((98, y + 34), dateline, font=mono, fill=(11, 15, 13))
    small = _font("SpaceMono-Bold.ttf", 30)
    draw.text((80, H - 96), "SWIPE →", font=small, fill=(244, 244, 241))
    draw.text((W - 80, H - 96), f"1/{count}", font=small, fill=(244, 244, 241), anchor="ra")
    return canvas


def compose_slide(art: bytes, caption: str, stamp: str, index: int, count: int) -> Image.Image:
    canvas = _cover_fit(Image.open(io.BytesIO(art)))
    _shade(canvas, top=False, strength=210, span=0.42)
    draw = ImageDraw.Draw(canvas)
    small = _font("SpaceMono-Bold.ttf", 30)
    draw.text((W - 80, 80), f"{index}/{count}", font=small, fill=(244, 244, 241), anchor="ra")
    font = _font("ArchivoBlack-Regular.ttf", 84)
    lines = _wrap(draw, (caption or "").upper(), font, W - 160)[:3]
    y = H - 110 - len(lines) * 92
    if stamp:
        mono = _font("SpaceMono-Bold.ttf", 32)
        draw.text((80, y - 58), stamp, font=mono, fill=(234, 255, 129))
    for line in lines:
        draw.text((80, y), line, font=font, fill=(244, 244, 241))
        y += 92
    return canvas


def make(
    client,
    version: dict,
    clips: dict[str, dict],
    asset_dirs: dict[str, Path],
    out_dir: Path,
    stage=None,
) -> dict:
    """Generate and typeset the carousel; returns the record stored on the version."""
    plan = montage.stored(version)
    shots = pick_shots(plan["shots"])
    if len(shots) < 2:
        raise ValueError("This reel needs at least two shots for a carousel.")
    frames = []
    for shot in shots:
        source = montage.normalized_clip(
            clips[shot["clip_id"]], asset_dirs[shot["clip_id"]], shot["slow"]
        )
        frames.append(frame_jpeg(source, shot["media_start"] + shot["duration"] / 2))
    texts = prompts(plan["style"], len(shots))
    references = [[data_url(f) for f in frames[:3]]] + [[data_url(f)] for f in frames]
    if stage:
        stage(f"Muse Image is designing {len(texts)} slides")
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs = [
            pool.submit(client.images, text, "1024x1280", refs)
            for text, refs in zip(texts, references, strict=True)
        ]
        arts = [job.result()[0] for job in jobs]
    if stage:
        stage("Typesetting your carousel")
    count = len(arts)
    date, _ = montage.date_lines(clips[shots[0]["clip_id"]])
    slides = [compose_cover(arts[0], plan["title"], date if plan["show_times"] else "", count)]
    for i, (shot, art) in enumerate(zip(shots, arts[1:], strict=True), start=2):
        stamp = montage.local_time(clips[shot["clip_id"]]) if plan["show_times"] else ""
        slides.append(compose_slide(art, shot["caption"], stamp, i, count))
    tmp = out_dir.with_name(out_dir.name + ".partial")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    names = []
    for i, slide in enumerate(slides, start=1):
        name = f"slide-{i:02d}.png"
        slide.save(tmp / name, optimize=True)
        names.append(name)
    with zipfile.ZipFile(tmp / "carousel.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            archive.write(tmp / name, name)
    shutil.rmtree(out_dir, ignore_errors=True)
    tmp.rename(out_dir)
    return {"slides": names, "style": plan["style"], "model": "muse-image-1.0"}
