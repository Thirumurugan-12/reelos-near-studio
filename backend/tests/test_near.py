"""NEAR reads never accept browser payment claims or return simulated success."""

import base64
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from reelos.api import create_app
from reelos.config import Settings
from reelos.near import NearReader, NearUnavailable

CONTRACT = "studio-escrow.testnet"
JOB_ID = "a" * 32
CONFIG = {
    "provider": "studio.testnet",
    "price": "100000000000000000000000",
    "storage_fee": "20000000000000000000000",
}
JOB = {
    "client": "customer.testnet",
    "amount": CONFIG["price"],
    "brief_hash": "b" * 64,
    "delivery_hash": None,
    "deadline_ns": "1900000000000000000",
    "status": "funded",
}


def reader(value, inspect=None):
    def respond(request):
        if inspect:
            inspect(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": "reelos",
                "result": {
                    "result": list(json.dumps(value).encode()),
                    "block_height": 123,
                    "block_hash": "final-block",
                },
            },
        )

    return NearReader(CONTRACT, transport=httpx.MockTransport(respond))


def test_rpc_uses_final_block_and_base64_arguments():
    def inspect(payload):
        assert payload["method"] == "query"
        params = payload["params"]
        assert params["finality"] == "final"
        assert params["account_id"] == CONTRACT
        assert params["method_name"] == "get_job"
        assert json.loads(base64.b64decode(params["args_base64"])) == {"job_id": JOB_ID}

    result = reader(JOB, inspect).get_job(JOB_ID)
    assert result["job"] == JOB
    assert result["block_height"] == 123
    assert result["network"] == "testnet"


def test_config_reads_price_from_chain_not_environment():
    assert reader(CONFIG).get_config()["config"] == CONFIG


def test_null_is_the_only_missing_job_response():
    assert reader(None).get_job(JOB_ID)["job"] is None


@pytest.mark.parametrize(
    "value",
    [
        True,
        {},
        {**JOB, "amount": 1.5},
        {**JOB, "status": "success"},
        {**JOB, "deadline_ns": "-1"},
        {**JOB, "amount": str(2**128)},
        {**JOB, "delivery_hash": "private footage URL"},
    ],
)
def test_malformed_contract_output_fails_closed(value):
    with pytest.raises(NearUnavailable):
        reader(value).get_job(JOB_ID)


@pytest.mark.parametrize("contract", ["studio.near", "https://evil.testnet", "../studio.testnet"])
def test_only_named_testnet_contracts_allowed(contract):
    with pytest.raises(ValueError):
        NearReader(contract)


def test_rpc_error_cannot_be_mistaken_for_missing_job():
    client = NearReader(
        CONTRACT,
        transport=httpx.MockTransport(
            lambda r: httpx.Response(200, json={"error": {"data": "private upstream details"}})
        ),
    )
    with pytest.raises(NearUnavailable, match="Unable to read"):
        client.get_job(JOB_ID)


def test_transport_failure_does_not_expose_upstream_details():
    def fail(request):
        raise httpx.ConnectError("secret upstream detail", request=request)

    client = NearReader(CONTRACT, transport=httpx.MockTransport(fail))
    with pytest.raises(NearUnavailable, match="Unable to read") as error:
        client.get_config()
    assert "secret" not in str(error.value)


def test_disabled_api_explains_missing_configuration(tmp_path):
    with TestClient(create_app(Settings(data_dir=tmp_path))) as client:
        result = client.get("/api/near/config")
        assert result.status_code == 200
        assert result.json() == {"enabled": False, "network": "testnet", "contract_id": None}
        assert client.get(f"/api/near/jobs/{JOB_ID}").status_code == 503


def test_api_returns_actual_chain_view_and_missing_job(tmp_path):
    app = create_app(Settings(data_dir=tmp_path, near_contract_id=CONTRACT))
    app.state.near_reader = reader(JOB)
    with TestClient(app) as client:
        response = client.get(f"/api/near/jobs/{JOB_ID}")
        assert response.status_code == 200
        assert response.json()["job"] == JOB
        app.state.near_reader = reader(None)
        assert client.get(f"/api/near/jobs/{JOB_ID}").status_code == 404
        assert client.get("/api/near/jobs/not-a-job").status_code == 422


def test_api_upstream_error_is_recoverable_502(tmp_path):
    app = create_app(Settings(data_dir=tmp_path, near_contract_id=CONTRACT))
    app.state.near_reader = reader({"status": "paid"})
    with TestClient(app) as client:
        response = client.get(f"/api/near/jobs/{JOB_ID}")
        assert response.status_code == 502
        assert response.json()["error"]["code"] == "NEAR_UNAVAILABLE"


@pytest.mark.parametrize(
    "result",
    [
        {"result": [999], "block_height": 123, "block_hash": "block"},
        {"result": [True], "block_height": 123, "block_hash": "block"},
        {"result": [], "block_height": 0, "block_hash": "block"},
        {"result": [], "block_height": True, "block_hash": "block"},
        {"result": [], "block_height": 123, "block_hash": ""},
        {"result": list(b"not json"), "block_height": 123, "block_hash": "block"},
    ],
)
def test_malformed_rpc_envelope_is_not_trusted(result):
    client = NearReader(
        CONTRACT,
        transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"result": result})),
    )
    with pytest.raises(NearUnavailable):
        client.get_job(JOB_ID)
