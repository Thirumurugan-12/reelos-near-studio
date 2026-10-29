import io
import json
import subprocess

import pytest
from PIL import Image, ImageDraw

from reelos.segmentation import subject_thumbnail


def test_subject_thumbnail_uses_actual_mask_frame_and_crops_to_subject(tmp_path):
    source = tmp_path / "proxy.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=red:s=100x200:r=10:d=1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(source),
        ],
        check=True,
    )
    track = tmp_path / "track"
    (track / "7").mkdir(parents=True)
    (track / "manifest.json").write_text(json.dumps({"fps": 10, "subjects": ["7"]}))
    mask = Image.new("L", (100, 200))
    ImageDraw.Draw(mask).rectangle((20, 40, 59, 119), fill=255)
    mask.save(track / "7" / "000005.png")
    preview = Image.open(io.BytesIO(subject_thumbnail(source, track, "7")))
    assert preview.size == (192, 192)
    r, g, b = preview.getpixel((96, 96))
    assert r > 180 and g < 40 and b < 40
    # The corners show darkened context rather than stretching the mask crop.
    assert preview.getpixel((0, 0))[0] < 120
    with pytest.raises(ValueError, match="subject"):
        subject_thumbnail(source, track, "8")


def test_subject_preview_requires_a_track_in_the_requested_project(tmp_path):
    from fastapi.testclient import TestClient

    from reelos.api import create_app
    from reelos.config import Settings
    from reelos.store import new_id

    app = create_app(Settings(data_dir=tmp_path))
    editor = app.state.editor
    with TestClient(app) as client:
        pid = client.post("/api/projects", json={"name": "Candidates"}).json()["id"]
        other = client.post("/api/projects", json={"name": "Other"}).json()["id"]
        asset = editor.store.put("asset", new_id(), {"project_id": pid})
        track_key = "a" * 32
        directory = editor.asset_dir(asset["id"])
        track = directory / "tracks" / track_key
        (track / "3").mkdir(parents=True)
        (track / "manifest.json").write_text(json.dumps({"fps": 10, "subjects": ["3"]}))
        Image.new("L", (100, 200), 255).save(track / "3" / "000000.png")
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-f",
                "lavfi",
                "-i",
                "color=blue:s=100x200:d=1",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(directory / "proxy.mp4"),
            ],
            check=True,
        )
        job = editor.store.put(
            "job",
            new_id(),
            {
                "project_id": pid,
                "status": "needs_subject",
                "request": {"asset_id": asset["id"]},
                "result": {"subjects": ["3"], "track_key": track_key},
            },
        )
        path = f"/jobs/{job['id']}/subjects/3/thumbnail"
        response = client.get(f"/api/projects/{pid}{path}")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert Image.open(io.BytesIO(response.content)).size == (192, 192)
        assert client.get(f"/api/projects/{other}{path}").status_code == 404
        assert client.get(f"/api/projects/{pid}{path.replace('/3/', '/99/')}").status_code == 404
