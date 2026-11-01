import copy

from fastapi.testclient import TestClient

from reelos.api import create_app
from reelos.config import Settings
from reelos.timeline import EditPlan


def test_reframe_creates_child_preserves_plan_and_reuses_tracking(tmp_path, monkeypatch):
    app = create_app(Settings(data_dir=tmp_path))
    with TestClient(app) as client:
        editor = app.state.editor
        pid = client.post("/api/projects", json={"name": "Framing"}).json()["id"]
        editor.store.put("asset", "a" * 32, {"project_id": pid, "role": "source", "duration": 20})
        parent = editor.version(pid, EditPlan(asset_id="a" * 32, source_out=20), track_key="cached")
        monkeypatch.setattr(editor.worker, "submit", lambda *args: None)
        result = client.post(
            f"/api/projects/{pid}/versions/{parent['id']}/framing",
            json={"scale": 0.82, "offset_y": 0.16},
        )
        assert result.status_code == 202
        job = result.json()
        child = editor.store.get("version", job["version_id"], pid)
        expected = copy.deepcopy(parent["plan"])
        expected["framing"] = {"scale": 0.82, "offset_y": 0.16}
        assert child["plan"] == expected
        assert child["parent_id"] == parent["id"] and child["track_key"] == "cached"
        assert child["render_profile"] == parent["render_profile"]
        assert editor.store.get("version", parent["id"], pid) == parent
        assert editor.store.get("project", pid)["current_version_id"] is None
        assert job["request"]["action"] == "render"
        assert editor.store.budget()["calls"] == []
        before = len(editor.store.list("version", pid))
        assert (
            client.post(
                f"/api/projects/{pid}/versions/{parent['id']}/framing",
                json={"scale": 1, "offset_y": 0},
            ).status_code
            == 422
        )
        assert len(editor.store.list("version", pid)) == before


def test_framing_rejects_cross_project_parent_and_invalid_geometry(tmp_path):
    app = create_app(Settings(data_dir=tmp_path))
    with TestClient(app) as client:
        editor = app.state.editor
        pid = client.post("/api/projects", json={"name": "Owner"}).json()["id"]
        other = client.post("/api/projects", json={"name": "Other"}).json()["id"]
        editor.store.put("asset", "a" * 32, {"project_id": pid, "role": "source", "duration": 20})
        parent = editor.version(pid, EditPlan(asset_id="a" * 32, source_out=20), track_key="cached")
        assert (
            client.post(
                f"/api/projects/{other}/versions/{parent['id']}/framing",
                json={"scale": 0.82, "offset_y": 0.16},
            ).status_code
            == 404
        )
        assert (
            client.post(
                f"/api/projects/{pid}/versions/{parent['id']}/framing",
                json={"scale": 0.9, "offset_y": 0.3},
            ).status_code
            == 422
        )
        assert len(editor.store.list("version", pid)) == 1
