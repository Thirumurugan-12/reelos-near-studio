import subprocess

import numpy as np
import pytest

from reelos.media import render
from reelos.timeline import EditPlan, validate_assets


def plan():
    return EditPlan.model_validate(
        {
            "asset_id": "a" * 32,
            "source_out": 1,
            "effects": [
                {
                    "id": "cutaway",
                    "type": "footage_insert",
                    "start": 0.2,
                    "end": 0.8,
                    "subject_id": "0",
                    "params": {"asset_id": "b" * 32, "source_in": 0.1},
                }
            ],
        }
    )


def test_insert_must_be_project_supporting_video_and_fit_its_duration():
    p = plan()
    main = {"a" * 32: {"duration": 1, "role": "source"}}
    supporting = {"duration": 1, "role": "supporting", "kind": "video"}
    validate_assets(p, main | {"b" * 32: supporting})
    for invalid in (
        None,
        supporting | {"role": "reference"},
        supporting | {"kind": "image"},
        supporting | {"duration": 0.5},
    ):
        assets = main | ({"b" * 32: invalid} if invalid else {})
        with pytest.raises(ValueError):
            validate_assets(p, assets)


def test_real_moving_cutaway_keeps_original_audio_and_restores_presenter(tmp_path):
    source = tmp_path / "main.mp4"
    supporting = tmp_path / "assets" / ("b" * 32) / "source.mp4"
    supporting.parent.mkdir(parents=True)
    for output, visual, tone in (
        (source, "color=c=red:s=180x320:r=30:d=1", 440),
        (supporting, "testsrc2=s=180x320:r=30:d=1", 880),
    ):
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                visual,
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency={tone}:duration=1",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                str(output),
            ],
            check=True,
        )
    output = tmp_path / "result.mp4"
    render(source, plan(), output, width=180, asset_root=tmp_path)
    frames = []
    for timestamp in (0.1, 0.3, 0.6, 0.9):
        result = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-ss",
                str(timestamp),
                "-i",
                str(output),
                "-frames:v",
                "1",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "pipe:1",
            ],
            capture_output=True,
            check=True,
        )
        frames.append(np.frombuffer(result.stdout, np.uint8).reshape(320, 180, 3))
    assert np.mean(frames[0][:, :, 0]) > 240
    assert np.mean(frames[3][:, :, 0]) > 240
    assert np.mean(abs(frames[1].astype(float) - frames[2])) > 2
    assert np.mean(frames[1][:, :, 1]) > 30
    audio = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(output),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "8000",
            "-f",
            "f32le",
            "pipe:1",
        ],
        capture_output=True,
        check=True,
    )
    samples = np.frombuffer(audio.stdout, np.float32)
    frequency = np.argmax(abs(np.fft.rfft(samples))) * 8000 / len(samples)
    assert 435 < frequency < 445

    original = output.read_bytes()
    supporting.write_text("invalid video")
    with pytest.raises(ValueError, match="cutaway"):
        render(source, plan(), output, width=180, asset_root=tmp_path)
    assert output.read_bytes() == original


def test_invalid_cutaway_reports_decode_failure(tmp_path):
    from reelos.footage import FootageTrack

    source = tmp_path / "bad.mp4"
    source.write_text("not a video")
    with FootageTrack(source, 0, 0.5, 180, 30) as track:
        with pytest.raises(ValueError, match="cutaway"):
            track.frame()
