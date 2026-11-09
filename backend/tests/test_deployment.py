import pytest
from fastapi.testclient import TestClient

import reelos.deployment as deployment
from reelos.api import create_app
from reelos.config import Settings


@pytest.fixture
def setup(tmp_path, monkeypatch):
    wasm = tmp_path / "escrow.wasm"
    wasm.write_bytes(b"\x00asm\x01\x00\x00\x00")
    env = tmp_path / ".env"
    env.write_text("MODEL_API_KEY=fixture-secret\n")
    monkeypatch.setattr(deployment, "ARTIFACT", wasm)
    monkeypatch.setattr(deployment, "ENV_FILE", env)
    app = create_app(Settings(data_dir=tmp_path / "data"))
    with TestClient(app) as client:
        yield client, app, env


def test_deployment_manifest_has_no_keys_and_serves_matching_artifact(setup):
    client, _, _ = setup
    info = client.get("/api/near/deployment").json()
    assert info["network"] == "testnet"
    assert info["deposit"] == "3000000000000000000000000"
    assert len(info["wasm_sha256"]) == 64
    assert client.get("/api/near/deployment/wasm").content.startswith(b"\x00asm")
    assert "private" not in str(info)


def mock_chain(monkeypatch, **changes):
    config = {
        "provider": "studio.testnet",
        "price": "100000000000000000000000",
        "storage_fee": "20000000000000000000000",
    } | changes
    monkeypatch.setattr(deployment.NearReader, "get_config", lambda self: {"config": config})
    monkeypatch.setattr(
        deployment,
        "inspect_contract",
        lambda id: {
            "code_hash": deployment.code_hash(deployment.ARTIFACT.read_bytes()),
            "keys": [],
        },
    )


def test_verified_keyless_contract_is_activated_without_touching_secrets(setup, monkeypatch):
    client, app, env = setup
    mock_chain(monkeypatch)
    r = client.post("/api/near/deployment/activate", json={"studio": "studio.testnet"})
    assert r.status_code == 200, r.text
    assert app.state.near_reader.contract_id == "escrow.studio.testnet"
    assert "MODEL_API_KEY=fixture-secret" in env.read_text()
    assert "REELOS_NEAR_CONTRACT_ID" in env.read_text()
    assert "fixture-secret" not in r.text


def test_wrong_provider_cannot_be_activated(setup, monkeypatch):
    client, app, env = setup
    mock_chain(monkeypatch, provider="stranger.testnet")
    assert (
        client.post("/api/near/deployment/activate", json={"studio": "studio.testnet"}).status_code
        == 422
    )
    assert app.state.near_reader is None
    assert "REELOS_NEAR_CONTRACT_ID" not in env.read_text()


def test_unexpected_code_or_keys_are_rejected(setup, monkeypatch):
    client, _, _ = setup
    mock_chain(monkeypatch)
    monkeypatch.setattr(
        deployment, "inspect_contract", lambda id: {"code_hash": "wrong", "keys": []}
    )
    assert (
        client.post("/api/near/deployment/activate", json={"studio": "studio.testnet"}).status_code
        == 422
    )
    monkeypatch.setattr(
        deployment,
        "inspect_contract",
        lambda id: {
            "code_hash": deployment.code_hash(deployment.ARTIFACT.read_bytes()),
            "keys": [{}],
        },
    )
    assert (
        client.post("/api/near/deployment/activate", json={"studio": "studio.testnet"}).status_code
        == 422
    )


def test_mainnet_wallet_rejected(setup):
    client, _, _ = setup
    assert (
        client.post("/api/near/deployment/activate", json={"studio": "studio.near"}).status_code
        == 422
    )
