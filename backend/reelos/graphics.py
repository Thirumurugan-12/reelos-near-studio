"""Render only approved, parameterized Remotion templates; never execute model code."""

import hashlib
import json
import math
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

from PIL import Image


def prepare_graphics(plan, root: Path) -> dict:
    directories, requests = {}, []
    for effect in plan.effects:
        if effect.type != "graphic_insert":
            continue
        props = effect.params.model_dump() | {"duration": effect.end - effect.start}
        key = hashlib.sha256(
            json.dumps({"renderer": "4.0.539-v1", "props": props}, sort_keys=True).encode()
        ).hexdigest()
        directory = root / "graphics" / key
        directories[effect.id] = directory
        if not (directory / "manifest.json").exists():
            requests.append({"props": props, "outputDir": str(directory)})
    if requests:
        script = Path(__file__).resolve().parents[2] / "graphics" / "render.mjs"
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
                raise ValueError(
                    "Graphic rendering failed. Your previous edit is preserved."
                ) from exc
    return {id: GraphicTrack(directory) for id, directory in directories.items()}


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
