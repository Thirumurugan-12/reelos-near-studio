"""A same-size replacement clip must not pass the frozen demo provenance check."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "demo-showcase/prepare_effect_gallery.py"


@pytest.fixture(scope="module")
def gallery_videos(tmp_path_factory):
    folder = tmp_path_factory.mktemp("gallery-videos")
    for color in ["red", "blue"]:
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-f",
                "lavfi",
                "-i",
                f"color={color}:s=432x768:r=30:d=3.2",
                "-frames:v",
                "96",
                "-c:v",
                "libx264",
                "-threads",
                "1",
                "-pix_fmt",
                "yuv420p",
                str(folder / f"{color}.mp4"),
            ],
            check=True,
        )
    return folder


@pytest.mark.parametrize("replacement", [False, True])
def test_gallery_verifies_frozen_clip_identity(tmp_path, gallery_videos, replacement):
    source = gallery_videos / "red.mp4"
    expected = hashlib.sha256(source.read_bytes()).hexdigest()
    clips = tmp_path / "assets/effect-gallery"
    clips.mkdir(parents=True)
    clip = gallery_videos / ("blue.mp4" if replacement else "red.mp4")
    (clips / "fx-01.mp4").write_bytes(clip.read_bytes())
    manifest = {
        "render_sha256": expected,
        "tiles": [{"asset": "fx-01.mp4", "sha256": expected}],
    }
    (tmp_path / "EFFECT_GALLERY.json").write_text(json.dumps(manifest))
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--target", str(tmp_path), "--source", str(source)],
        capture_output=True,
        text=True,
    )
    if replacement:
        assert result.returncode != 0, "Wrong footage passed the demo verification"
        assert "identity mismatch" in result.stderr
        assert (clips / "fx-01.mp4").read_bytes() == clip.read_bytes()
    else:
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["verified_clips"] == 1
