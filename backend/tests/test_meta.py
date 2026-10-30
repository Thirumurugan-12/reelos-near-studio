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
