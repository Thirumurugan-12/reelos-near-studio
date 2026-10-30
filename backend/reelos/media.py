"""Streaming media decode, subject-aware composition, and audio-preserving export."""

import json
import math
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from reelos.timeline import EditPlan

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def inspect_media(path: Path) -> dict:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
            capture_output=True,
            timeout=20,
            check=True,
        )
        info = json.loads(result.stdout)
        video = next(s for s in info["streams"] if s["codec_type"] == "video")
        duration = float(info["format"]["duration"])
        width, height = int(video["width"]), int(video["height"])
        if not math.isfinite(duration) or duration <= 0 or not 0 < width * height <= 3840 * 2160:
            raise ValueError("unsupported media dimensions or duration")
        return {
            "duration": duration,
            "width": width,
            "height": height,
            "has_audio": any(s["codec_type"] == "audio" for s in info["streams"]),
        }
    except (subprocess.SubprocessError, ValueError, KeyError, StopIteration) as exc:
        raise ValueError("Cannot decode this video; use a supported MP4 or MOV.") from exc


def portrait_filter(width: int, fps: int) -> str:
    height = width * 16 // 9
    return (
        f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1"
    )


def make_proxy(source: Path, output: Path, fps: int = 10, portrait: bool = True) -> None:
    filters = (
        portrait_filter(360, fps)
        if portrait
        else (
            f"fps={fps},scale=640:640:force_original_aspect_ratio=decrease:force_divisible_by=2,setsar=1"
        )
    )
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-i",
            str(source),
            "-vf",
            filters,
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-c:a",
            "aac",
            "-b:a",
            "64k",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ],
        capture_output=True,
        timeout=180,
        check=True,
    )


def font(size: int, family: str = "aileron"):
    if family == "system":  # Legacy development artifacts retain their original policy.
        for path in FONT_CANDIDATES:
            if Path(path).is_file():
                return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def text_layer(
    size: tuple,
    style,
    time: float,
    start: float,
    end: float,
    font_family: str = "aileron",
    badge: bool = False,
) -> Image.Image:
    width, height = size
    layer = Image.new("RGBA", size)
    draw = ImageDraw.Draw(layer)
    face = font(max(10, round(height * style.size)), font_family)
    # Short editorial titles should keep one line at every output resolution.
    if len(style.text) <= 24:
        while face.size > 5 and draw.textlength(style.text, font=face) > width * 0.88:
            face = font(max(5, face.size - 1), font_family)
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
    while face.size > 5 and draw.multiline_textbbox((0, 0), text, font=face)[2] > width * 0.9:
        face = font(max(5, face.size - 1), font_family)
    if draw.multiline_textbbox((0, 0), text, font=face)[2] > width * 0.9:
        raise ValueError("Use shorter text or add spaces so the headline fits the frame.")
    entrance = min(1.0, max(0, (time - start) / 0.4))
    eased = 1 - (1 - entrance) ** 3
    alpha = round(255 * min(eased, max(0, (end - time) / 0.15)))
    x, y = width * style.x, height * (style.y + 0.02 * (1 - eased))
    bounds = draw.multiline_textbbox((0, 0), text, font=face, spacing=4, align="center")
    tw, th = bounds[2] - bounds[0], bounds[3] - bounds[1]
    x = max(tw / 2 + 4, min(width - tw / 2 - 4, x))
    y = max(th / 2 + 4, min(height - th / 2 - 4, y))
    color = tuple(bytes.fromhex(style.color[1:])) + (alpha,)
    if badge:
        padding = height * 0.013
        draw.rounded_rectangle(
            (
                x - tw / 2 - padding,
                y - th / 2 - padding,
                x + tw / 2 + padding,
                y + th / 2 + padding,
            ),
            radius=height * 0.01,
            fill=(15, 23, 18, round(alpha * 0.85)),
        )
    draw.multiline_text(
        (x - tw / 2, y - th / 2 - bounds[1]),
        text,
        font=face,
        fill=color,
        align="center",
        spacing=4,
        stroke_width=1,
        stroke_fill=(0, 0, 0, alpha // 3),
    )
    return layer


def composite(
    frame: Image.Image,
    plan: EditPlan,
    time: float,
    masks: dict,
    font_family: str = "aileron",
    graphics: dict | None = None,
) -> np.ndarray:
    original = frame.convert("RGBA")
    current = original.copy()
    active = [e for e in plan.effects if e.start <= time < e.end]
    # Fixed layer order makes combined effects independent of planner array order.
    for effect in active:
        mask = masks.get(effect.subject_id)
        if mask is None:
            continue  # Missing tracked frame means subject absent; never guess another subject.
        if effect.type == "subject_spotlight":
            style = effect.params
            if style.background == "black":
                dark = Image.blend(current, Image.new("RGBA", frame.size, "black"), style.intensity)
            else:
                backdrop = (
                    current.convert("L").convert("RGBA")
                    if style.background == "monochrome"
                    else current
                )
                dark = ImageEnhance.Brightness(backdrop).enhance(1 - style.intensity)
            current = Image.composite(current, dark, mask.filter(ImageFilter.GaussianBlur(1)))
    for effect in active:
        mask = masks.get(effect.subject_id)
        if mask is not None and effect.type == "behind_subject_text":
            layer = text_layer(
                frame.size, effect.params, time, effect.start, effect.end, font_family
            )
            with_text = Image.alpha_composite(current, layer)
            current = Image.composite(current, with_text, mask)
    for effect in active:
        mask = masks.get(effect.subject_id)
        if (
            mask is not None
            and effect.type == "subject_spotlight"
            and effect.params.outline_width > 0
        ):
            # Bound morphology cost at the source-mask resolution, including for 1080p exports.
            width = min(360, frame.width)
            size = (width, round(frame.height * width / frame.width))
            local = mask.resize(size, Image.Resampling.BILINEAR)
            radius = max(1, round(width * effect.params.outline_width))
            edge = ImageChops.subtract(local.filter(ImageFilter.MaxFilter(radius * 2 + 1)), local)
            halo = ImageChops.subtract(local.filter(ImageFilter.GaussianBlur(radius * 4)), local)
            halo = halo.point(lambda p: round(p * effect.params.glow))
            alpha = ImageChops.add(edge, halo).resize(frame.size, Image.Resampling.BILINEAR)
            current = Image.composite(
                Image.new("RGBA", frame.size, effect.params.outline_color), current, alpha
            )
    for effect in active:
        mask = masks.get(effect.subject_id)
        if mask is not None and effect.type == "tracked_label":
            bounds = mask.getbbox()
            if bounds:
                dx, dy = mask.info.get("label_motion", (0, 0))
                style = effect.params.model_copy(
                    update={
                        "x": max(0.05, min(0.95, effect.params.x + dx)),
                        "y": max(0.05, min(0.95, effect.params.y + dy)),
                    }
                )
                current = Image.alpha_composite(
                    current,
                    text_layer(
                        frame.size, style, time, effect.start, effect.end, font_family, badge=True
                    ),
                )
    for effect in active:
        if effect.type == "graphic_insert":
            if not graphics or effect.id not in graphics:
                raise ValueError("Graphic insert is missing its rendered Remotion asset.")
            current = graphics[effect.id].at(time - effect.start, frame.size)
    return np.asarray(current.convert("RGB"))


def frame_subject(frame: Image.Image, masks: dict, framing) -> tuple[Image.Image, dict]:
    if framing.scale == 1 and framing.offset_y == 0:
        return frame, masks
    width, height = frame.size
    size = (round(width * framing.scale), round(height * framing.scale))
    position = ((width - size[0]) // 2, round(height * framing.offset_y))
    backdrop = ImageEnhance.Brightness(
        frame.filter(ImageFilter.GaussianBlur(width * 0.05))
    ).enhance(0.35)
    backdrop.paste(frame.resize(size, Image.Resampling.LANCZOS), position)
    transformed = {}
    for subject, mask in masks.items():
        canvas = Image.new("L", frame.size)
        canvas.paste(mask.resize(size, Image.Resampling.BILINEAR), position)
        if "label_motion" in mask.info:
            canvas.info["label_motion"] = tuple(
                v * framing.scale for v in mask.info["label_motion"]
            )
        transformed[subject] = canvas
    return backdrop, transformed


def headline_visibility(
    size: tuple, effect, mask: Image.Image, font_family: str = "aileron"
) -> float:
    time = (effect.start + effect.end) / 2
    alpha = (
        np.asarray(
            text_layer(size, effect.params, time, effect.start, effect.end, font_family).getchannel(
                "A"
            )
        )
        > 32
    )
    total = np.count_nonzero(alpha)
    if not total:
        return 0
    return float(np.count_nonzero(alpha & (np.asarray(mask) < 128)) / total)


class MaskTrack:
    """Masks use normalized portrait source time, not edited output frame indices."""

    def __init__(self, directory: Path):
        self.directory = directory
        self.manifest = json.loads((directory / "manifest.json").read_text())
        self.fps = self.manifest["fps"]
        self.subjects = self.manifest["subjects"]
        self._cached_read = lru_cache(maxsize=24)(self._read)
        self.reference = {}
        for subject in self.subjects:
            paths = sorted((directory / subject).glob("*.png"))
            if paths:
                image = self._cached_read(subject, int(paths[0].stem))
                self.reference[subject] = self._anchor(image)

    def _read(self, subject: str, frame: int):
        path = self.directory / subject / f"{frame:06d}.png"
        if not path.exists():
            return None
        with Image.open(path) as image:
            return image.convert("L")

    @staticmethod
    def _anchor(image):
        bounds = image.getbbox() if image else None
        if not bounds:
            return None
        return ((bounds[0] + bounds[2]) / (2 * image.width), bounds[3] / image.height)

    def at(self, seconds: float, size: tuple) -> dict:
        frame = math.floor(seconds * self.fps + 1e-6)
        result = {}
        for subject in self.subjects:
            image = self._cached_read(subject, frame)
            if image is not None:
                mask = image.resize(size, Image.Resampling.BILINEAR)
                recent = [
                    self._anchor(self._cached_read(subject, f))
                    for f in range(max(0, frame - 2), frame + 1)
                ]
                anchors = [a for a in recent if a is not None]
                ref = self.reference.get(subject)
                if anchors and ref:
                    mask.info["label_motion"] = tuple(
                        sum(a[i] for a in anchors) / len(anchors) - ref[i] for i in range(2)
                    )
                result[subject] = mask
        return result


def render(
    source: Path,
    plan: EditPlan,
    output: Path,
    width: int = 1080,
    track: MaskTrack | None = None,
    progress=None,
    font_family: str = "aileron",
    graphics: dict | None = None,
) -> None:
    if any(e.type != "graphic_insert" for e in plan.effects) and track is None:
        raise ValueError("Subject effects require a real tracking artifact.")
    if track and any(e.subject_id not in track.subjects for e in plan.effects):
        raise ValueError("Selected subject is absent from tracking artifact.")
    height = width * 16 // 9
    count = round(plan.duration * plan.fps)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Temporary output is promoted atomically only after decoder and encoder succeed.
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        part = Path(temp) / "render.mp4"
        with (
            (Path(temp) / "decode.log").open("w+b") as dec_log,
            (Path(temp) / "encode.log").open("w+b") as enc_log,
        ):
            decoder = subprocess.Popen(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-ss",
                    str(plan.source_in),
                    "-i",
                    str(source),
                    "-an",
                    "-vf",
                    portrait_filter(width, plan.fps),
                    "-frames:v",
                    str(count),
                    "-pix_fmt",
                    "rgb24",
                    "-f",
                    "rawvideo",
                    "pipe:1",
                ],
                stdout=subprocess.PIPE,
                stderr=dec_log,
            )
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
                    f"{width}x{height}",
                    "-r",
                    str(plan.fps),
                    "-i",
                    "pipe:0",
                    "-ss",
                    str(plan.source_in),
                    "-i",
                    str(source),
                    "-map",
                    "0:v",
                    "-map",
                    "1:a:0?",
                    "-t",
                    str(count / plan.fps),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "20",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    "-movflags",
                    "+faststart",
                    str(part),
                ],
                stdin=subprocess.PIPE,
                stderr=enc_log,
            )
            try:
                for index in range(count):
                    raw = decoder.stdout.read(width * height * 3)
                    if len(raw) != width * height * 3:
                        raise ValueError("Decoder ended before the requested source interval.")
                    image = Image.frombytes("RGB", (width, height), raw)
                    t = index / plan.fps
                    masks = track.at(plan.source_in + t, image.size) if track else {}
                    image, masks = frame_subject(image, masks, plan.framing)
                    for effect in plan.effects:
                        midpoint = round((effect.start + effect.end) * plan.fps / 2)
                        if effect.type == "behind_subject_text" and index == midpoint:
                            mask = masks.get(effect.subject_id)
                            if (
                                mask is not None
                                and headline_visibility(image.size, effect, mask, font_family) < 0.4
                            ):
                                raise ValueError(
                                    "The headline is mostly hidden by the subject. "
                                    "Move it into clear space or use a framed layout."
                                )
                    encoder.stdin.write(
                        composite(image, plan, t, masks, font_family, graphics).tobytes()
                    )
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
