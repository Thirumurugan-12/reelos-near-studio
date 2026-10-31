import json

import httpx
import pytest

from reelos.config import Settings
from reelos.meta import MetaClient
from reelos.store import Store


def test_incomplete_response_keeps_usage_and_terminal_reason(tmp_path, monkeypatch):
    real = httpx.Client
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "status": "incomplete",
                "incomplete_details": {"reason": "max_output_tokens"},
                "usage": {"output_tokens": 64},
                "output": [],
            },
        )
    )
    monkeypatch.setattr(httpx, "Client", lambda **kw: real(transport=transport, **kw))
    store = Store(tmp_path)
    with pytest.raises(ValueError, match="max_output_tokens"):
        MetaClient(Settings(api_key="test"), store).response("test", [])
    assert store.budget()["calls"][0]["usage"] == {"output_tokens": 64}
    assert store.budget()["calls"][0]["status"] == "incomplete"
    cached = list((tmp_path / "responses").glob("*.json"))
    assert len(cached) == 1
    assert json.loads(cached[0].read_text())["incomplete_details"]["reason"] == "max_output_tokens"


def test_transcription_records_billed_audio_duration(tmp_path, monkeypatch):
    real = httpx.Client
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "transcript": "An actual transcript.",
                "audioDurationMs": 20400,
                "turns": [],
            },
        )
    )
    monkeypatch.setattr(httpx, "Client", lambda **kw: real(transport=transport, **kw))
    source = tmp_path / "audio.wav"
    source.write_bytes(b"audio fixture; network is mocked")
    store = Store(tmp_path)
    result = MetaClient(Settings(api_key="test"), store).transcribe(source)
    assert result["transcript"] == "An actual transcript."
    assert store.budget()["calls"][0]["usage"]["audio_duration_ms"] == 20400
    assert store.budget()["calls"][0]["estimated_usd"] == pytest.approx(0.001)


def test_provider_error_keeps_diagnostic_reason_without_key(tmp_path, monkeypatch):
    real = httpx.Client
    key = "LLM_123_private_secret"
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            402,
            json={
                "error": {
                    "code": "billing_not_configured",
                    "type": "billing_error",
                    "message": "Check account " + key,
                }
            },
        )
    )
    monkeypatch.setattr(httpx, "Client", lambda **kw: real(transport=transport, **kw))
    store = Store(tmp_path)
    with pytest.raises(ValueError, match="billing_not_configured") as exc:
        MetaClient(Settings(api_key=key), store).response("test", [])
    assert key not in str(exc.value)
    errors = list((tmp_path / "responses").glob("*.error.json"))
    assert len(errors) == 1
    record = errors[0].read_text()
    assert "billing_not_configured" in record and key not in record
    assert len(store.budget()["calls"]) == 1


def test_file_availability_distinguishes_missing_file_from_access_error(tmp_path, monkeypatch):
    real = httpx.Client
    status = 404
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            status,
            json={
                "error": {
                    "code": "file_not_found" if status == 404 else "permission_denied",
                    "message": "Unavailable",
                }
            },
        )
    )
    monkeypatch.setattr(httpx, "Client", lambda **kw: real(transport=transport, **kw))
    client = MetaClient(Settings(api_key="test"), Store(tmp_path))
    assert client.file_available("file-old") is False
    status = 200
    assert client.file_available("file-new") is True
    status = 403
    with pytest.raises(ValueError, match="403"):
        client.file_available("file-private")
    assert client.store.budget()["calls"] == []
