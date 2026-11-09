"""Public-clone demo must exercise the real editor without credentials or model calls."""

import hashlib
import importlib.util
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from reelos.api import create_app
from reelos.meta import MetaClient


def demo_module():
    path = Path(__file__).parents[1] / "scripts" / "reviewer_demo.py"
    spec = importlib.util.spec_from_file_location("reviewer_demo", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_demo_renders_real_export_without_provider_or_wallet(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_API_KEY", "must-not-be-used")
    monkeypatch.setenv("REELOS_API_BUDGET_USD", "150")
    monkeypatch.setenv("REELOS_NEAR_CONTRACT_ID", "unrelated.testnet")

    def forbidden(*args, **kwargs):
        pytest.fail("Reviewer sample must not call Meta")

    for method in ("upload", "response", "transcribe", "images"):
        monkeypatch.setattr(MetaClient, method, forbidden)
    demo = demo_module()
    result = demo.seed(tmp_path)
    assert result["kind"] == "generated-local-render"
    assert result["model_calls"] == 0
    assert result["chain_transactions"] == 0
    assert result["media"]["width"] == 1080
    assert result["media"]["height"] == 1920
    assert result["media"]["has_audio"]
    assert result["media"]["duration"] == pytest.approx(4, abs=0.05)
    settings = demo.settings(tmp_path)
    assert not settings.api_key and settings.budget_usd == 0
    assert settings.near_contract_id == "reelos-escrow-20261109.testnet"
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/health").json()["budget_limit_usd"] == 0
        project = client.get(f"/api/projects/{result['project_id']}").json()
        assert "Generated" in project["name"]
        assert project["current_version_id"] == result["version_id"]
        export = client.get(result["export_url"])
        assert export.status_code == 200
        assert export.headers["content-type"] == "video/mp4"
        assert hashlib.sha256(export.content).hexdigest() == result["sha256"]
    with pytest.raises(ValueError, match="empty"):
        demo.seed(tmp_path)
