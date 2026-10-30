import io
import subprocess

from fastapi.testclient import TestClient

from reelos.api import create_app
from reelos.config import Settings


def test_long_source_upload_is_preserved_but_reference_limit_remains(tmp_path):
    source = tmp_path / "long.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=blue:s=90x160:r=10:d=65",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-pix_fmt",
            "yuv420p",
            str(source),
        ],
        check=True,
    )
    with TestClient(create_app(Settings(data_dir=tmp_path / "store"))) as client:
        pid = client.post("/api/projects", json={"name": "Full source"}).json()["id"]

        def upload(role):
            return client.post(
                f"/api/projects/{pid}/assets",
                files={
                    "file": ("long.mp4", io.BytesIO(source.read_bytes()), "video/mp4"),
                },
                data={"role": role},
            )

        response = upload("source")
        assert response.status_code == 201
        assert response.json()["duration"] == 65
        assert upload("reference").status_code == 422
        aid = response.json()["id"]
        short_full = client.post(
            f"/api/projects/{pid}/versions",
            json={
                "plan": {
                    "asset_id": aid,
                    "source_out": 19.5,
                    "output_mode": "full",
                }
            },
        )
        assert short_full.status_code == 422
        assert "entire source" in short_full.json()["error"]["message"]
