import hashlib
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from reelos.api import create_app
from reelos.config import Settings

ID = "a" * 32
CLIENT = "customer.testnet"
CONFIG = {
    "provider": "studio.testnet",
    "price": "100000000000000000000000",
    "storage_fee": "20000000000000000000000",
}


class Chain:
    def __init__(self):
        self.job = None

    def get_config(self):
        return {
            "enabled": True,
            "network": "testnet",
            "contract_id": "escrow.testnet",
            "config": CONFIG,
        }

    def get_job(self, id):
        return {"job": self.job}


@pytest.fixture
def setup(tmp_path):
    app = create_app(Settings(data_dir=tmp_path, near_contract_id="escrow.testnet"))
    chain = Chain()
    app.state.near_reader = chain
    e = app.state.editor
    pid, aid = "b" * 32, "c" * 32
    e.store.put("project", pid, {"name": "Paid demo"})
    e.store.put(
        "asset",
        aid,
        {
            "project_id": pid,
            "role": "source",
            "name": "source.mp4",
            "duration": 1,
            "width": 180,
            "height": 320,
            "has_audio": False,
        },
    )
    e.asset_dir(aid).mkdir(parents=True)
    (e.asset_dir(aid) / "source.mp4").write_bytes(b"fixture source")
    with TestClient(app) as client:
        yield client, e, chain, pid, aid


def create(setup):
    client, e, chain, pid, aid = setup
    response = client.post(
        f"/api/projects/{pid}/orders",
        json={
            "id": ID,
            "client": CLIENT,
            "asset_id": aid,
            "instruction": "Add a title",
            "subject_prompt": "person",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def fund(chain, order, **changes):
    chain.job = {
        "client": CLIENT,
        "amount": CONFIG["price"],
        "brief_hash": order["brief_hash"],
        "deadline_ns": order["deadline_ns"],
        "status": "funded",
        "delivery_hash": None,
    } | changes


def test_order_idempotent_and_cannot_be_reused_for_different_brief(setup):
    order = create(setup)
    assert order == create(setup)
    assert len(setup[0].get(f"/api/projects/{setup[3]}/orders").json()) == 1
    client, _, _, pid, aid = setup
    response = client.post(
        f"/api/projects/{pid}/orders",
        json={"id": ID, "client": CLIENT, "asset_id": aid, "instruction": "Different brief"},
    )
    assert response.status_code == 422


def test_no_render_without_confirmed_funding(setup):
    order = create(setup)
    client, e, _, pid, _ = setup
    assert client.post(f"/api/projects/{pid}/orders/{order['id']}/start").status_code == 422
    assert not e.store.list("job", pid)


@pytest.mark.parametrize(
    "changes",
    [
        {"client": "stranger.testnet"},
        {"brief_hash": "d" * 64},
        {"amount": "1"},
        {"status": "refunded"},
        {"deadline_ns": "1"},
    ],
)
def test_tampered_or_wrong_funding_cannot_start_render(setup, changes):
    order = create(setup)
    client, e, chain, pid, _ = setup
    fund(chain, order, **changes)
    assert client.post(f"/api/projects/{pid}/orders/{ID}/start").status_code == 422
    assert not e.store.list("job", pid)


def test_funded_render_is_dispatched_only_once(setup, monkeypatch):
    order = create(setup)
    client, e, chain, pid, _ = setup
    fund(chain, order)
    calls = []
    monkeypatch.setattr(e, "run", lambda job: calls.append(job["id"]))
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(
            pool.map(lambda _: client.post(f"/api/projects/{pid}/orders/{ID}/start"), range(4))
        )
    assert all(r.status_code == 200 for r in responses)
    e.worker.shutdown(wait=True)
    assert calls == [ID]
    assert len(e.store.list("job", pid)) == 1


def test_source_change_blocks_paid_render(setup):
    order = create(setup)
    client, e, chain, pid, aid = setup
    fund(chain, order)
    (e.asset_dir(aid) / "source.mp4").write_bytes(b"changed")
    assert client.post(f"/api/projects/{pid}/orders/{ID}/start").status_code == 422


def test_completed_render_has_artifact_hash(setup):
    order = create(setup)
    client, e, chain, pid, _ = setup
    fund(chain, order)
    vid = "d" * 32
    e.store.put("job", ID, {"project_id": pid, "status": "completed", "version_id": vid})
    e.store.put("version", vid, {"project_id": pid, "has_preview": True})
    e.version_dir(vid).mkdir(parents=True)
    (e.version_dir(vid) / "preview.mp4").write_bytes(b"rendered preview")
    result = client.get(f"/api/projects/{pid}/orders/{ID}").json()
    assert result["delivery_hash"] == hashlib.sha256(b"rendered preview").hexdigest()


def test_cross_project_order_not_accessible(setup):
    create(setup)
    client, e, _, _, _ = setup
    other = "e" * 32
    e.store.put("project", other, {"name": "Other"})
    assert client.get(f"/api/projects/{other}/orders/{ID}").status_code == 404
    assert client.get(f"/api/projects/{other}/orders").json() == []


def test_cannot_attach_a_paid_order_to_an_existing_editor_job(setup):
    client, editor, _, pid, _ = setup
    editor.store.put("job", ID, {"project_id": pid, "status": "completed"})
    response = client.post(
        f"/api/projects/{pid}/orders",
        json={"id": ID, "client": CLIENT, "asset_id": "c" * 32, "instruction": "Add a title"},
    )
    assert response.status_code == 422


def test_config_change_blocks_a_previously_funded_order(setup):
    order = create(setup)
    client, _, chain, pid, _ = setup
    fund(chain, order)
    chain.get_config = lambda: {"contract_id": "another.testnet", "config": CONFIG}
    assert client.post(f"/api/projects/{pid}/orders/{ID}/start").status_code == 422


def test_existing_failed_job_is_not_automatically_repeated(setup, monkeypatch):
    order = create(setup)
    client, e, chain, pid, _ = setup
    fund(chain, order)
    e.store.put("job", ID, {"project_id": pid, "order_id": ID, "status": "failed"})
    monkeypatch.setattr(e, "run", lambda job: pytest.fail("Must not retry paid work"))
    assert client.post(f"/api/projects/{pid}/orders/{ID}/start").json()["status"] == "failed"


def test_paid_order_renders_real_export_without_paid_model_calls(setup, monkeypatch):
    import subprocess
    import time

    from reelos.timeline import EditPlan

    client, e, chain, pid, aid = setup
    source = e.asset_dir(aid) / "source.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
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
    monkeypatch.setattr(e, "segment", lambda *args: ({"subjects": ["1"]}, None))
    monkeypatch.setattr(e, "provider_file", lambda *args: "fixture")
    monkeypatch.setattr(e, "source_speech", lambda *args: None)
    monkeypatch.setattr(
        "reelos.service.create_plan",
        lambda *args, **kwargs: (EditPlan(asset_id=aid, source_in=0, source_out=0.6), []),
    )
    order = create(setup)
    fund(chain, order)
    assert client.post(f"/api/projects/{pid}/orders/{ID}/start").status_code == 200
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        result = client.get(f"/api/projects/{pid}/orders/{ID}").json()
        if result["render"]["status"] in {"completed", "failed"}:
            break
        time.sleep(0.05)
    assert result["render"]["status"] == "completed", result
    assert len(result["delivery_hash"]) == 64
    video = client.get(result["preview_url"])
    assert video.status_code == 200 and video.headers["content-type"] == "video/mp4"
    assert not e.store.budget()["calls"]
