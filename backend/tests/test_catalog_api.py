import io

from fastapi.testclient import TestClient
from PIL import Image

from reelos.api import create_app
from reelos.config import Settings


def test_effect_catalog_is_discoverable_and_previews_are_bounded(tmp_path):
    with TestClient(create_app(Settings(data_dir=tmp_path))) as c:
        r = c.get("/api/effects")
        assert r.status_code == 200
        rows = r.json()["effects"]
        assert len(rows) == 45
        assert all("id" in x and "options" in x for x in rows)
        assert c.get("/api/effects/not-a-recipe/preview").status_code == 404


def test_supporting_image_upload_and_project_isolation(tmp_path):
    with TestClient(create_app(Settings(data_dir=tmp_path))) as c:
        p = c.post("/api/projects", json={"name": "Images"}).json()["id"]
        image = io.BytesIO()
        Image.new("RGB", (400, 300), "red").save(image, format="PNG")
        r = c.post(
            f"/api/projects/{p}/assets",
            data={"role": "supporting"},
            files={"file": ("card.png", image.getvalue(), "image/png")},
        )
        assert r.status_code == 201, r.text
        asset = r.json()
        assert asset["kind"] == "image" and asset["role"] == "supporting"
        assert (
            c.get(f"/api/projects/{p}/assets/{asset['id']}/source").headers["content-type"]
            == "image/png"
        )
        other = c.post("/api/projects", json={"name": "Other"}).json()["id"]
        assert c.get(f"/api/projects/{other}/assets/{asset['id']}/source").status_code == 404
        bad = c.post(
            f"/api/projects/{p}/versions", json={"plan": {"asset_id": asset["id"], "source_out": 2}}
        )
        assert bad.status_code == 422


def test_explicit_apply_creates_child_without_mutating_parent(tmp_path, monkeypatch):
    from reelos.timeline import EditPlan

    app = create_app(Settings(data_dir=tmp_path))
    with TestClient(app) as c:
        editor = app.state.editor
        pid = c.post("/api/projects", json={"name": "Apply"}).json()["id"]
        asset = editor.store.put(
            "asset", "a" * 32, {"project_id": pid, "role": "source", "duration": 5}
        )
        parent = editor.version(
            pid, EditPlan(asset_id=asset["id"], source_out=5), track_key="tracking"
        )
        original = parent["plan"]
        monkeypatch.setattr(editor.worker, "submit", lambda *args: None)
        response = c.post(
            f"/api/projects/{pid}/effects",
            json={
                "version_id": parent["id"],
                "start": 1,
                "end": 4,
                "params": {"fx": "orbit", "options": {"count": 4}},
            },
        )
        assert response.status_code == 202, response.text
        child = editor.store.get("version", response.json()["version_id"], pid)
        assert child["parent_id"] == parent["id"] and child["track_key"] == parent["track_key"]
        assert child["plan"]["effects"][0]["params"]["fx"] == "orbit"
        assert editor.store.get("version", parent["id"], pid)["plan"] == original
