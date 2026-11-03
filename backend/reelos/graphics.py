"""Render only approved, parameterized graphic templates; never execute model code.

Two renderers produce the same on-disk contract (PNG frames plus manifest.json):
HyperFrames (default) and the original Remotion templates (fallback).
"""

import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

from PIL import Image

FPS = 30
GRAPHICS_DIR = Path(__file__).resolve().parents[2] / "graphics"
HYPERFRAMES_VERSION = "0.9.4"
RENDERER_IDS = {"remotion": "4.0.539-v1", "hyperframes": f"hyperframes-{HYPERFRAMES_VERSION}-v1"}
DURATION_MARKER = 'data-duration="3.000000"'
GROUND = (8, 8, 8)
FAILED = "Graphic rendering failed. Your previous edit is preserved."
# The renderer child gets only what it needs: no model credentials, no telemetry or self-updates.
CHILD_ENV_KEEP = ("PATH", "HOME", "TMPDIR", "LANG", "HYPERFRAMES_BROWSER_PATH")
CHILD_ENV_FLAGS = {
    "HYPERFRAMES_NO_TELEMETRY": "1",
    "HF_CLI_TELEMETRY_DISABLED": "1",
    "DO_NOT_TRACK": "1",
    "HYPERFRAMES_NO_UPDATE_CHECK": "1",
    "HYPERFRAMES_NO_AUTO_INSTALL": "1",
    "HYPERFRAMES_NO_OPTIONAL_INSTALL": "1",
    "HYPERFRAMES_NO_CAPTURE_DOTENV": "1",
}


def frame_count(duration: float) -> int:
    # Same length rule as the Remotion composition's calculateMetadata.
    return max(6, math.ceil(duration * FPS))


def prepare_graphics(plan, root: Path, renderer: str = "hyperframes") -> dict:
    if renderer not in RENDERER_IDS:
        raise ValueError(f"Unknown graphics renderer: {renderer}")
    directories, requests = {}, []
    for effect in plan.effects:
        if effect.type != "graphic_insert":
            continue
        props = effect.params.model_dump() | {"duration": effect.end - effect.start}
        # Layout is composited over the presenter; the underlying art is reusable.
        props.pop("presentation", None)
        key = hashlib.sha256(
            json.dumps(
                {"renderer": RENDERER_IDS[renderer], "props": props}, sort_keys=True
            ).encode()
        ).hexdigest()
        directory = root / "graphics" / key
        directories[effect.id] = directory
        if not (directory / "manifest.json").exists():
            requests.append({"props": props, "outputDir": str(directory)})
    if requests:
        if renderer == "hyperframes":
            _render_hyperframes(requests)
        else:
            _render_remotion(requests)
    return {id: GraphicTrack(directory) for id, directory in directories.items()}


def _render_remotion(requests: list) -> None:
    script = GRAPHICS_DIR / "render.mjs"
    with tempfile.TemporaryDirectory() as temp:
        request = Path(temp) / "request.json"
        request.write_text(json.dumps(requests))
        try:
            subprocess.run(
                ["node", str(script), str(request)],
                cwd=script.parent,
                capture_output=True,
                check=True,
                timeout=300,
            )
        except subprocess.SubprocessError as exc:
            raise ValueError(FAILED) from exc


def hyperframes_binary() -> Path:
    return GRAPHICS_DIR / "node_modules" / ".bin" / "hyperframes"


def _child_env() -> dict:
    env = {key: os.environ[key] for key in CHILD_ENV_KEEP if key in os.environ}
    return env | CHILD_ENV_FLAGS


def hyperframes_command(project: Path, output: Path, props: dict) -> list:
    variables = {key: props[key] for key in ("template", "title", "body", "accent")}
    return [
        str(hyperframes_binary()),
        "render",
        str(project),
        "--format",
        "png-sequence",
        "-o",
        str(output),
        # Model-written copy only ever travels as JSON variables bound with textContent.
        "--variables",
        json.dumps(variables),
        "--workers",
        "1",
        "--quiet",
    ]


def _render_hyperframes(requests: list) -> None:
    template = GRAPHICS_DIR / "hyperframes"
    if not hyperframes_binary().exists() or not (template / "index.html").exists():
        raise ValueError(FAILED)
    for request in requests:
        props, target = request["props"], Path(request["outputDir"])
        frames = frame_count(float(props["duration"]))
        with tempfile.TemporaryDirectory() as temp:
            project, output = Path(temp) / "project", Path(temp) / "out"
            shutil.copytree(template, project)
            index = project / "index.html"
            html = index.read_text()
            if html.count(DURATION_MARKER) != 2:
                raise ValueError(FAILED)
            index.write_text(html.replace(DURATION_MARKER, f'data-duration="{frames / FPS:.6f}"'))
            try:
                subprocess.run(
                    hyperframes_command(project, output, props),
                    cwd=temp,
                    env=_child_env(),
                    capture_output=True,
                    check=True,
                    timeout=180,
                )
            except subprocess.SubprocessError as exc:
                raise ValueError(FAILED) from exc
            rendered = sorted(output.glob("*.png")) if output.is_dir() else []
            if len(rendered) < frames:
                raise ValueError(FAILED)
            write_frames(rendered[:frames], target, props)


def write_frames(rendered: list, target: Path, props: dict) -> None:
    """Flatten RGBA captures onto the opaque ground and publish the manifest last."""
    target.mkdir(parents=True, exist_ok=True)
    names = []
    for index, path in enumerate(rendered):
        name = f"frame-{index:04d}.png"
        with Image.open(path) as frame:
            rgba = frame.convert("RGBA")
            flat = Image.new("RGB", rgba.size, GROUND)
            flat.paste(rgba, mask=rgba.getchannel("A"))
            flat.save(target / name)
        names.append(name)
    (target / "manifest.json").write_text(
        json.dumps(
            {
                "fps": FPS,
                "frames": names,
                "props": props,
                "renderer": f"HyperFrames {HYPERFRAMES_VERSION}",
            }
        )
    )


class GraphicTrack:
    def __init__(self, directory: Path):
        self.directory = directory
        self.manifest = json.loads((directory / "manifest.json").read_text())
        self._cached = lru_cache(maxsize=2)(self._read)

    def _read(self, index):
        with Image.open(self.directory / self.manifest["frames"][index]) as frame:
            return frame.convert("RGB")

    def at(self, seconds: float, size: tuple):
        index = min(
            len(self.manifest["frames"]) - 1,
            max(0, math.floor(seconds * self.manifest["fps"] + 1e-6)),
        )
        return self._cached(index).resize(size, Image.Resampling.LANCZOS)
