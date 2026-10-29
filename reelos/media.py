"""Streaming media decode, subject-aware composition, and audio-preserving export."""

import json
import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from reelos.timeline import EditPlan

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def inspect_media(path: Path) -> dict:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json",
             str(path)], capture_output=True, timeout=20, check=True,
        )
        info = json.loads(result.stdout)
        video = next(s for s in info["streams"] if s["codec_type"] == "video")
        duration = float(info["format"]["duration"])
        width, height = int(video["width"]), int(video["height"])
        if not math.isfinite(duration) or duration <= 0 or not 0 < width * height <= 3840 * 2160:
            raise ValueError("unsupported media dimensions or duration")
        return {"duration": duration, "width": width, "height": height,
                "has_audio": any(s["codec_type"] == "audio" for s in info["streams"])}
    except (subprocess.SubprocessError, ValueError, KeyError, StopIteration) as exc:
        raise ValueError("Cannot decode this video; use a supported MP4 or MOV.") from exc


def portrait_filter(width: int, fps: int) -> str:
    height = width * 16 // 9
    return (f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1")


def make_proxy(source: Path, output: Path, fps: int = 10) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-vf",
                    portrait_filter(360, fps), "-an", "-c:v", "libx264", "-preset",
                    "veryfast", "-pix_fmt", "yuv420p", str(output)],
                   capture_output=True, timeout=180, check=True)


def font(size: int):
    for path in FONT_CANDIDATES:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def text_layer(size: tuple, style, time: float, start: float, end: float) -> Image.Image:
    width, height = size
    layer = Image.new("RGBA", size)
    draw = ImageDraw.Draw(layer)
    face = font(max(10, round(height * style.size)))
    # Fit bounded lines rather than silently crop long user text.
    words, lines, line = style.text.split(), [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if draw.textlength(candidate, font=face) > width * 0.9 and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    lines.append(line)
    text = "\n".join(lines)
    while draw.multiline_textbbox((0, 0), text, font=face)[2] > width * 0.9:
        face = font(max(5, face.size - 1))
    entrance = min(1.0, max(0, (time - start) / 0.4))
    eased = 1 - (1 - entrance) ** 3
    alpha = round(255 * min(eased, max(0, (end - time) / 0.15)))
    x, y = width * style.x, height * (style.y + 0.02 * (1 - eased))
    bounds = draw.multiline_textbbox((0, 0), text, font=face, spacing=4, align="center")
    tw, th = bounds[2] - bounds[0], bounds[3] - bounds[1]
    x = max(tw / 2 + 4, min(width - tw / 2 - 4, x))
    y = max(th / 2 + 4, min(height - th / 2 - 4, y))
    color = tuple(bytes.fromhex(style.color[1:])) + (alpha,)
    draw.multiline_text((x - tw / 2, y - th / 2 - bounds[1]), text, font=face,
                        fill=color, align="center", spacing=4, stroke_width=1,
                        stroke_fill=(0, 0, 0, alpha // 3))
    return layer


def composite(frame: Image.Image, plan: EditPlan, time: float, masks: dict) -> np.ndarray:
    original = frame.convert("RGBA")
    current = original.copy()
    active = [e for e in plan.effects if e.start <= time < e.end]
    # Fixed layer order makes combined effects independent of planner array order.
    for effect in active:
        mask = masks.get(effect.subject_id)
        if mask is None:
            continue  # Missing tracked frame means subject absent; never guess another subject.
        if effect.type == "subject_spotlight":
            dark = ImageEnhance.Brightness(current).enhance(1 - effect.params.intensity)
            current = Image.composite(current, dark, mask.filter(ImageFilter.GaussianBlur(1)))
    for effect in active:
        mask = masks.get(effect.subject_id)
        if mask is not None and effect.type == "behind_subject_text":
            layer = text_layer(frame.size, effect.params, time, effect.start, effect.end)
            with_text = Image.alpha_composite(current, layer)
            current = Image.composite(current, with_text, mask)
    for effect in active:
        mask = masks.get(effect.subject_id)
        if mask is not None and effect.type == "tracked_label":
            bounds = mask.getbbox()
            if bounds:
                style = effect.params.model_copy(update={
                    "x": ((bounds[0] + bounds[2]) / 2) / frame.width,
                    "y": min(0.9, bounds[3] / frame.height + 0.04),
                })
                current = Image.alpha_composite(
                    current, text_layer(frame.size, style, time, effect.start, effect.end),
                )
    return np.asarray(current.convert("RGB"))


class MaskTrack:
    """Masks use normalized portrait source time, not edited output frame indices."""

    def __init__(self, directory: Path):
        self.directory = directory
        self.manifest = json.loads((directory / "manifest.json").read_text())
        self.fps = self.manifest["fps"]
        self.subjects = self.manifest["subjects"]

    def at(self, seconds: float, size: tuple) -> dict:
        frame = math.floor(seconds * self.fps + 1e-6)
        result = {}
        for subject in self.subjects:
            path = self.directory / subject / f"{frame:06d}.png"
            if path.exists():
                with Image.open(path) as image:
                    result[subject] = image.convert("L").resize(size, Image.Resampling.BILINEAR)
        return result


def render(source: Path, plan: EditPlan, output: Path, width: int = 1080,
           track: MaskTrack | None = None, progress=None) -> None:
    if plan.effects and track is None:
        raise ValueError("Subject effects require a real tracking artifact.")
    if track and any(e.subject_id not in track.subjects for e in plan.effects):
        raise ValueError("Selected subject is absent from tracking artifact.")
    height = width * 16 // 9
    count = round(plan.duration * plan.fps)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Temporary output is promoted atomically only after decoder and encoder succeed.
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        part = Path(temp) / "render.mp4"
        with (Path(temp) / "decode.log").open("w+b") as dec_log, \
                (Path(temp) / "encode.log").open("w+b") as enc_log:
            decoder = subprocess.Popen([
                "ffmpeg", "-v", "error", "-ss", str(plan.source_in), "-i", str(source),
                "-an", "-vf", portrait_filter(width, plan.fps), "-frames:v", str(count),
                "-pix_fmt", "rgb24", "-f", "rawvideo", "pipe:1",
            ], stdout=subprocess.PIPE, stderr=dec_log)
            encoder = subprocess.Popen([
                "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                "-s", f"{width}x{height}", "-r", str(plan.fps), "-i", "pipe:0",
                "-ss", str(plan.source_in), "-i", str(source), "-map", "0:v",
                "-map", "1:a:0?", "-t", str(count / plan.fps), "-c:v", "libx264",
                "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-movflags", "+faststart", str(part),
            ], stdin=subprocess.PIPE, stderr=enc_log)
            try:
                for index in range(count):
                    raw = decoder.stdout.read(width * height * 3)
                    if len(raw) != width * height * 3:
                        raise ValueError("Decoder ended before the requested source interval.")
                    image = Image.frombytes("RGB", (width, height), raw)
                    t = index / plan.fps
                    masks = track.at(plan.source_in + t, image.size) if track else {}
                    encoder.stdin.write(composite(image, plan, t, masks).tobytes())
                    if progress and index % 15 == 0:
                        progress(index / count)
                encoder.stdin.close()
                if decoder.wait(timeout=30) or encoder.wait(timeout=90):
                    raise ValueError("Media encoding failed.")
                part.replace(output)
            finally:
                for process in (decoder, encoder):
                    if process.poll() is None:
                        process.kill()
                    process.wait()
                decoder.stdout.close()
                if not encoder.stdin.closed:
                    encoder.stdin.close()
