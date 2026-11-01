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


def test_full_video_preserves_audio_tail_after_last_camera_frame(tmp_path):
    source = tmp_path / "audio-tail.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=blue:s=90x160:r=30:d=1",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1.1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(source),
        ],
        check=True,
    )
    duration = inspect_media(source)["duration"]
    output = tmp_path / "complete.mp4"
    render(
        source,
        EditPlan(asset_id="a" * 32, source_out=duration, output_mode="full"),
        output,
        width=90,
    )
    meta = inspect_media(output)
    assert meta["has_audio"]
    assert abs(meta["duration"] - duration) <= 1 / 30
    count = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=nb_frames",
            "-of",
            "csv=p=0",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert int(count.stdout.strip()) == round(duration * 30)


@pytest.mark.parametrize("occlusion_fraction", [0.25, 0.75])
def test_rejects_headline_hidden_away_from_midpoint(source, tmp_path, occlusion_fraction):
    """A moving subject can clear the midpoint but cover the title earlier/later."""
    plan = EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_in": 0.2,
            "source_out": 0.8,
            "effects": [
                {
                    "id": "title",
                    "type": "behind_subject_text",
                    "start": 0.1,
                    "end": 0.5,
                    "subject_id": "0",
                    "params": {"text": "YOUR STORY", "y": 0.1},
                }
            ],
        }
    )

    class MovingTrack:
        subjects = ["0"]

        def at(self, seconds, size):
            covered_at = plan.source_in + 0.1 + 0.4 * occlusion_fraction
            covered = abs(seconds - covered_at) < 1 / 60
            return {"0": Image.new("L", size, 255 if covered else 0)}

    output = tmp_path / "existing.mp4"
    output.write_bytes(b"previous playable version")
    with pytest.raises(ValueError, match="headline is mostly hidden"):
        render(source, plan, output, width=180, track=MovingTrack())
    assert output.read_bytes() == b"previous playable version"
