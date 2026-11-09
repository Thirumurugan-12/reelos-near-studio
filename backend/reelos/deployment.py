"""Local deployment review and verification; no signing keys or transaction broadcasting."""

import hashlib
from pathlib import Path

import httpx
from dotenv import set_key
from fastapi.responses import FileResponse, JSONResponse

from reelos.near import TESTNET_RPC, Account, NearReader, NearUnavailable
from reelos.timeline import Contract

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT / "contracts/reelos-escrow/target/wasm32-unknown-unknown/release/reelos_escrow.wasm"
ENV_FILE = ROOT / ".env"
DEPOSIT = "3000000000000000000000000"
PRICE = "100000000000000000000000"
STORAGE = "20000000000000000000000"


class ActivateDeployment(Contract):
    studio: Account


def code_hash(code):
    raw = hashlib.sha256(code).digest()
    value = int.from_bytes(raw, "big")
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    result = ""
    while value:
        value, digit = divmod(value, 58)
        result = alphabet[digit] + result
    return "1" * (len(raw) - len(raw.lstrip(b"\0"))) + result


def inspect_contract(account):
    try:
        with httpx.Client(timeout=15, follow_redirects=False) as client:
            values = []
            for request in ("view_account", "view_access_key_list"):
                response = client.post(
                    TESTNET_RPC,
                    json={
                        "jsonrpc": "2.0",
                        "id": "deployment",
                        "method": "query",
                        "params": {
                            "request_type": request,
                            "finality": "final",
                            "account_id": account,
                        },
                    },
                )
                response.raise_for_status()
                value = response.json()
                if value.get("error"):
                    raise ValueError("RPC error")
                values.append(value["result"])
        return {"code_hash": values[0]["code_hash"], "keys": values[1]["keys"]}
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise NearUnavailable("Cannot verify deployment yet. Wait and try again.") from None


def mount_deployment(app, settings):
    @app.get("/api/near/deployment")
    def manifest():
        if not ARTIFACT.is_file():
            return JSONResponse(
                {
                    "error": {
                        "code": "WASM_MISSING",
                        "message": "Build the escrow Wasm before deploying.",
                    }
                },
                503,
            )
        wasm = ARTIFACT.read_bytes()
        return {
            "network": "testnet",
            "deposit": DEPOSIT,
            "price": PRICE,
            "storage_fee": STORAGE,
            "wasm_bytes": len(wasm),
            "wasm_sha256": hashlib.sha256(wasm).hexdigest(),
            "wasm_url": "/api/near/deployment/wasm",
            "initializer": "new_for_studio",
        }

    @app.get("/api/near/deployment/wasm")
    def wasm():
        if not ARTIFACT.is_file():
            raise KeyError("Build artifact not found")
        return FileResponse(ARTIFACT, media_type="application/wasm")

    @app.post("/api/near/deployment/activate")
    def activate(data: ActivateDeployment):
        account = f"escrow.{data.studio}"
        if not data.studio.endswith(".testnet") or len(account) > 64:
            raise ValueError("Choose a named NEAR testnet studio account.")
        if settings.near_contract_id and settings.near_contract_id != account:
            raise ValueError(
                "A different escrow is already configured. Review it before switching."
            )
        if not ARTIFACT.is_file():
            raise ValueError("Build the escrow Wasm before activating it.")
        expected_hash = code_hash(ARTIFACT.read_bytes())
        reader = NearReader(account)
        config = reader.get_config()["config"]
        if config != {"provider": data.studio, "price": PRICE, "storage_fee": STORAGE}:
            raise ValueError("Deployed studio or pricing does not match the reviewed plan.")
        onchain = inspect_contract(account)
        if onchain["code_hash"] != expected_hash or onchain["keys"] != []:
            raise ValueError("Expected the reviewed Wasm and a keyless escrow account.")
        set_key(str(ENV_FILE), "REELOS_NEAR_CONTRACT_ID", account, quote_mode="never")
        settings.near_contract_id = account
        app.state.near_reader = reader
        return {"enabled": True, "network": "testnet", "contract_id": account, "config": config}
