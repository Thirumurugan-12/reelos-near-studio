from fastapi.testclient import TestClient

from reelos.api import create_app
from reelos.config import Settings


def test_export_metadata_update_does_not_reorder_created_versions(tmp_path):
    app = create_app(Settings(data_dir=tmp_path))
    with TestClient(app) as client:
        pid = client.post("/api/projects", json={"name": "Stable history"}).json()["id"]
        store = app.state.editor.store
        old = store.put(
            "version", "a" * 32, {"project_id": pid, "created_at": 1, "has_export": False}
        )
        newer = store.put(
            "version", "b" * 32, {"project_id": pid, "created_at": 2, "has_export": False}
        )
        store.put("version", old["id"], old | {"has_export": True})
        versions = client.get(f"/api/projects/{pid}").json()["versions"]
        assert [v["id"] for v in versions] == [newer["id"], old["id"]]
        assert versions[1]["has_export"]
