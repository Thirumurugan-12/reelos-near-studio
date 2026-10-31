"""SAM-backed bridge for the attributed 45-effect library; no upstream tracker or CLI."""

import subprocess
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
from PIL import Image

from reelos.vendor import claude_effects as fx

cv2.setNumThreads(1)

GLOBAL_FX = {"moody", "swipe", "uninstall", "dot-reveal"}


def head_anchor(image, mask, detector=None):
    """Use an actual local face detection intersecting the SAM-selected person."""
    w, h = image.size
    binary = np.asarray(mask) > 127
    if detector is not None:
        detector.setInputSize((w, h))
        _, faces = detector.detect(
            cv2.cvtColor(np.asarray(image.convert("RGB")), cv2.COLOR_RGB2BGR)
        )
        candidates = []
        for face in faces if faces is not None else []:
            x, y, fw, fh = face[:4]
            cx, cy = x + fw / 2, y + fh / 2
            if 0 <= int(cx) < w and 0 <= int(cy) < h and binary[int(cy), int(cx)]:
                candidates.append((float(fw * fh * face[-1]), (float(cx), float(cy), float(fw))))
        if candidates:
            return max(candidates)[1]
    # Disappearance never gets a guessed person. The fallback is an explicit SAM-head estimate.
    bounds = mask.getbbox()
    if not bounds:
        return None
    x0, y0, x1, y1 = bounds
    band = binary[y0 : min(h, y0 + max(4, round((y1 - y0) * 0.18)))]
    xs = np.where(band.any(0))[0]
    if not len(xs):
        return None
    fw = max(w * 0.08, min(w * 0.6, (np.percentile(xs, 95) - np.percentile(xs, 5)) * 0.75))
    return float(np.median(xs)), float(y0 + fw * 0.7), float(fw)


def _context(image, mask, time, elapsed, anchor):
    c = SimpleNamespace(
        W=image.width,
        H=image.height,
        t=time,
        lt=elapsed,
        fps=30,
        img=np.asarray(image.convert("RGB"), dtype=np.float32) / 255,
        m=np.asarray(mask, dtype=np.float32) / 255,
    )
    c.fx, c.fy, c.fw = anchor
    return c


class CatalogRenderer:
    def __init__(self, plan, cards=None, starts=None):
        self.plan = plan
        self.cards = cards or {}
        self.starts = starts or {}
        self.states = {}
        self.detector = cv2.FaceDetectorYN.create(
            str(Path(__file__).with_name("vendor") / "models/yunet.onnx"),
            "",
            (320, 320),
            0.65,
            0.3,
            100,
        )
        self.anchor_cache = {}

    def _anchor(self, image, mask, time, subject):
        key = (subject, round(time * 30), image.size)
        if key not in self.anchor_cache:
            self.anchor_cache[key] = head_anchor(image, mask, self.detector)
            if len(self.anchor_cache) > 64:
                del self.anchor_cache[next(iter(self.anchor_cache))]
        return self.anchor_cache[key]

    def _effect(self, e, image, mask, anchor):
        if e.id in self.states:
            return self.states[e.id]
        options = dict(e.params.options)
        if e.params.text:
            options["text"] = e.params.text
        # Replace upstream attribution/fictional social-proof defaults with neutral content.
        for key, value in {
            "handle": "@creator",
            "name": "Creator",
            "role": "creator",
            "item": "Your pick",
            "chip": "ReelOS",
            "reply": "Thanks for watching",
            "sub": "Your story, edited",
            "board": "Your clips",
            "issue": "THE CREATOR ISSUE",
            "others": "Option A|Option B|Option C",
        }.items():
            options.setdefault(key, value)
        if e.params.fx == "headline-wall":
            options.setdefault("text", "Your opening::|Your story::|Your closing::")
            options.setdefault("total", "STORY NOTES")
            options.setdefault("label", "YOUR IDEAS")
        if e.params.fx == "place-in-grid":
            options.setdefault("views", "|".join(["—"] * 9))
        supplied = self.cards.get(e.id)
        if e.params.fx == "profile-wall":
            has_count = "count" in options
            options.setdefault("count", max(1, len(supplied or [])))
            options.setdefault("label", "total" if has_count else "source frames")
        # Preserve the value types expected by the upstream helpers.
        if e.params.fx == "over-the-shoulder-zoom":
            options.setdefault("text", "First metric|Second metric")
        for key in ("from", "to", "ticks", "views", "total", "bars", "donut", "kpi"):
            if key in options:
                options[key] = (
                    int(float(options[key]))
                    if key == "from" and e.params.fx == "countdown-flip"
                    else str(options[key])
                )
        if supplied:
            options["images"] = "project-assets" if e.params.media_ids else "source-frames"
        instance = SimpleNamespace(
            name=e.params.fx,
            start=e.start,
            end=e.end,
            d=e.end - e.start,
            o=options,
            state={},
            cards=supplied or [image.copy()],
        )
        start_image, start_mask, start_anchor = self.starts.get(e.id, (image, mask, anchor))
        if e.params.fx == "pause-point":
            instance.state["f"] = (
                np.asarray(start_image, dtype=np.float32) / 255,
                np.asarray(start_mask, dtype=np.float32) / 255,
                *start_anchor,
            )
        cx, cy, fw = start_anchor
        r = max(2, fw * 0.9)
        x0, y0 = max(0, int(cx - r)), max(0, int(cy - r * 1.05))
        instance.state["face"] = start_image.crop(
            (
                x0,
                y0,
                min(start_image.width, int(x0 + r * 2)),
                min(start_image.height, int(y0 + r * 2)),
            )
        ).convert("RGBA")
        if e.params.fx == "match-cut":
            instance.state["anchor"] = (
                image.width / 2,
                max(image.height * 0.1, (cy - fw * 1.55) * image.height / start_image.height),
            )
        self.states[e.id] = instance
        return instance

    def apply(self, image, time, masks):
        active = [
            e for e in self.plan.effects if e.type == "catalog_effect" and e.start <= time < e.end
        ]
        for id in list(self.states):
            e = next(e for e in self.plan.effects if e.id == id)
            if not e.start <= time < e.end:
                del self.states[id]
        if not active:
            return image
        context = None
        for effect in active:
            mask = masks.get(effect.subject_id)
            if mask is None or not mask.getbbox():
                if effect.params.fx not in GLOBAL_FX:
                    continue
                mask = Image.new("L", image.size)
                anchor = (image.width / 2, image.height * 0.3, image.width * 0.2)
            else:
                anchor = self._anchor(image, mask, time, effect.subject_id)
            if anchor is None:
                continue
            if context is None:
                context = _context(image, mask, time, time - effect.start, anchor)
            context.lt = time - effect.start
            instance = self._effect(effect, image, mask, anchor)
            fx.EFFECTS[instance.name][0](context, instance)
        if context is None:
            return image
        return Image.fromarray((np.clip(context.img, 0, 1) * 255 + 0.5).astype("uint8"))


def source_frame(source, time, size):
    from reelos.media import portrait_filter

    result = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            str(time),
            "-i",
            str(source),
            "-frames:v",
            "1",
            "-vf",
            portrait_filter(size[0], 30),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "pipe:1",
        ],
        capture_output=True,
        check=True,
        timeout=30,
    )
    if len(result.stdout) != size[0] * size[1] * 3:
        raise ValueError("Cannot read supporting media frame.")
    return Image.frombytes("RGB", size, result.stdout)


def prepare_catalog(plan, source, root, width, track, font_family="aileron", graphics=None):
    from reelos.media import composite, frame_subject

    recipes = [e for e in plan.effects if e.type == "catalog_effect"]
    if not recipes:
        return None
    size = (width, width * 16 // 9)
    thumbs = [
        source_frame(source, plan.source_in + plan.duration * (i + 0.5) / 9, (360, 640))
        for i in range(9)
    ]
    cards, starts = {}, {}
    media_cache = {}
    renderer = CatalogRenderer(plan)
    for e in recipes:
        cards[e.id] = []
        for id in e.params.media_ids:
            if root is None:
                raise ValueError("Supporting assets require the project media store.")
            directory = root / "assets" / id
            if id not in media_cache:
                if (directory / "source.png").exists():
                    with Image.open(directory / "source.png") as im:
                        media_cache[id] = im.convert("RGB").copy()
                else:
                    from reelos.media import inspect_media

                    duration = inspect_media(directory / "source.mp4")["duration"]
                    media_cache[id] = source_frame(
                        directory / "source.mp4", min(1, duration / 2), (360, 640)
                    )
            cards[e.id].append(media_cache[id])
        cards[e.id] = cards[e.id] or thumbs
        snapshot_size = size if e.params.fx == "pause-point" else (360, 640)
        frame = source_frame(source, plan.source_in + e.start, snapshot_size)
        masks = track.at(plan.source_in + e.start, snapshot_size) if track else {}
        frame, masks = frame_subject(frame, masks, plan.framing)
        frame = Image.fromarray(composite(frame, plan, e.start, masks, font_family, graphics))
        mask = masks.get(e.subject_id)
        if mask is not None:
            anchor = renderer._anchor(frame, mask, plan.source_in + e.start, e.subject_id)
            if anchor:
                starts[e.id] = (frame, mask, anchor)
    renderer.cards = cards
    renderer.starts = starts
    return renderer
