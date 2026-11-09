import hashlib
import json

import pytest
from fastapi.testclient import TestClient

import reelos.rehearsal as rehearsal
from reelos.api import create_app
from reelos.config import Settings


@pytest.fixture
def prepared(tmp_path, monkeypatch):
    output = tmp_path / "demo.mp4"
    output.write_bytes(b"local verified render fixture")
    spec = {
        "client": "customer.testnet",
        "contract_id": "escrow.testnet",
        "job_id": "a" * 32,
        "brief_hash": "b" * 64,
        "deadline_ns": "1794400000000000000",
        "delivery_hash": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    manifest = tmp_path / "rehearsal.json"
    manifest.write_text(json.dumps(spec))
    monkeypatch.setattr(rehearsal, "MANIFEST", manifest)
    monkeypatch.setattr(rehearsal, "OUTPUT", output)
    app = create_app(Settings(data_dir=tmp_path / "data", near_contract_id="escrow.testnet"))
    monkeypatch.setattr(
        app.state.near_reader,
        "get_config",
        lambda: {
            "contract_id": "escrow.testnet",
            "config": {
                "provider": "studio.testnet",
                "price": "100000000000000000000000",
                "storage_fee": "20000000000000000000000",
            },
        },
    )
    chain = {
        "client": spec["client"],
        "brief_hash": spec["brief_hash"],
        "deadline_ns": spec["deadline_ns"],
        "amount": "100000000000000000000000",
        "status": "funded",
        "delivery_hash": None,
    }
    monkeypatch.setattr(
        app.state.near_reader,
        "get_job",
        lambda id: {"job": chain, "block_height": 123, "block_hash": "test-block"},
    )
    return TestClient(app), output, chain, manifest, spec


def test_rehearsal_binds_actual_output_to_distinct_finalized_roles(prepared):
    client, _, _, _, spec = prepared
    r = client.get("/api/near/rehearsal")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["delivery_hash"] == spec["delivery_hash"]
    assert data["provider"] == "studio.testnet"
    assert data["client"] == "customer.testnet"
    assert data["total_deposit"] == "120000000000000000000000"
    assert data["mode"] == "contract_rehearsal"


def test_changed_output_or_chain_brief_blocks_signing_data(prepared):
    client, output, chain, _, _ = prepared
    chain["brief_hash"] = "c" * 64
    assert client.get("/api/near/rehearsal").status_code == 422
    chain["brief_hash"] = "b" * 64
    output.write_bytes(b"changed after review")
    assert client.get("/api/near/rehearsal").status_code == 422


def test_provider_cannot_be_the_customer_in_distinct_role_rehearsal(prepared):
    client, _, _, manifest, spec = prepared
    manifest.write_text(json.dumps(spec | {"client": "studio.testnet"}))
    assert client.get("/api/near/rehearsal").status_code == 422
