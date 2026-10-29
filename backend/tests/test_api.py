import io
import subprocess

import pytest
from fastapi.testclient import TestClient

from reelos.api import create_app
from reelos.config import Settings


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(Settings(data_dir=tmp_path))) as client:
        yield client


def test_rejects_cross_origin_mutations(client):
    response = client.post(
        "/api/projects", json={"name": "test"}, headers={"Origin": "https://evil.example"}
    )
    assert response.status_code == 403


def test_upload_rejects_invalid_video_and_preserves_project(client):
    project = client.post("/api/projects", json={"name": "My reel"}).json()
    response = client.post(
        f"/api/projects/{project['id']}/assets",
        files={"file": ("bad.mp4", io.BytesIO(b"bad media"), "video/mp4")},
    )
    assert response.status_code == 422
    assert client.get(f"/api/projects/{project['id']}").json()["assets"] == []


def test_real_upload_and_manual_render_job(client, tmp_path):
    source = tmp_path / "fixture.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=blue:s=180x320:r=30:d=1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(source),
        ],
        check=True,
    )
    project = client.post("/api/projects", json={"name": "Fixture"}).json()
    pid = project["id"]
    with source.open("rb") as file:
        asset = client.post(f"/api/projects/{pid}/assets", files={"file": file}).json()
    plan = {"asset_id": asset["id"], "source_in": 0, "source_out": 0.6}
    version = client.post(f"/api/projects/{pid}/versions", json={"plan": plan}).json()
    job = client.post(
        f"/api/projects/{pid}/jobs",
        json={
            "action": "render",
            "version_id": version["id"],
            "quality": "preview",
        },
    ).json()
    # A condition-based bounded poll; rendering is a real background job.
    import time

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        status = client.get(f"/api/projects/{pid}/jobs/{job['id']}").json()
        if status["status"] in {"completed", "failed"}:
            break
        time.sleep(0.02)
    assert status["status"] == "completed", status
    output = client.get(f"/api/projects/{pid}/versions/{version['id']}/preview")
    assert output.status_code == 200 and output.headers["content-type"] == "video/mp4"
    other = client.post("/api/projects", json={"name": "Other"}).json()["id"]
    assert client.get(f"/api/projects/{other}/assets/{asset['id']}/source").status_code == 404
