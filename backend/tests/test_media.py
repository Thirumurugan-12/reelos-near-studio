import subprocess

import numpy as np
import pytest
from PIL import Image

from reelos.media import inspect_media, render
from reelos.timeline import EditPlan


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "source.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=c=red:s=180x320:r=30:d=1",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(path),
        ],
        check=True,
    )
    return path


def test_renders_real_trimmed_video_with_audio(source, tmp_path):
    plan = EditPlan(asset_id="a" * 32, source_in=0.2, source_out=0.8)
    output = tmp_path / "out.mp4"
    render(source, plan, output, width=180)
    meta = inspect_media(output)
    assert meta["width"] == 180 and meta["height"] == 320
    assert abs(meta["duration"] - 0.6) < 0.1
    assert meta["has_audio"]


def test_rejects_bad_media(tmp_path):
    path = tmp_path / "bad.mp4"
    path.write_text("not a video")
    with pytest.raises(ValueError, match="decode"):
        inspect_media(path)


def test_headline_composites_behind_foreground():
    from reelos.media import composite

    data = {
        "asset_id": "a" * 32,
        "source_out": 1,
        "effects": [
            {
                "id": "title",
                "type": "behind_subject_text",
                "start": 0,
                "end": 1,
                "subject_id": "0",
                "params": {"text": "MMMMMM", "y": 0.5, "size": 0.15},
            }
        ],
    }
    plan = EditPlan.model_validate(data)
    frame = Image.new("RGB", (180, 320), "red")
    full = Image.new("L", frame.size, 255)
    empty = Image.new("L", frame.size, 0)
    assert np.array_equal(composite(frame, plan, 0.5, {"0": full}), np.array(frame))
    result = composite(frame, plan, 0.5, {"0": empty})
    assert (result[:, :, 1] > 100).sum() > 50


def test_subject_effects_require_real_tracking_artifact(source, tmp_path):
    data = {
        "asset_id": "a" * 32,
        "source_out": 0.5,
        "effects": [
            {"id": "light", "type": "subject_spotlight", "start": 0, "end": 0.5, "subject_id": "0"}
        ],
    }
    with pytest.raises(ValueError, match="tracking"):
        render(source, EditPlan.model_validate(data), tmp_path / "out.mp4", width=180)
