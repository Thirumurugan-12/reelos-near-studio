"""Read-only finalized contract state. This module never signs or broadcasts transactions."""

import base64
import json
import re
from typing import Annotated, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

TESTNET_RPC = "https://rpc.testnet.near.org"
ACCOUNT = r"^(([a-z0-9]+[-_])*[a-z0-9]+\.)*([a-z0-9]+[-_])*[a-z0-9]+$"
Account = Annotated[str, Field(pattern=ACCOUNT, min_length=2, max_length=64)]
Amount = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]{0,38})$")]
Timestamp = Annotated[str, Field(pattern=r"^[1-9][0-9]{0,19}$")]
Digest = Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


class ChainValue(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)


class ChainConfig(ChainValue):
    provider: Account
    price: Amount
    storage_fee: Amount

    @model_validator(mode="after")
    def bounds(self):
        if not 0 < int(self.price) < 2**128 or not 0 < int(self.storage_fee) < 2**128:
            raise ValueError("Invalid contract amounts")
        return self


class ChainJob(ChainValue):
    client: Account
    amount: Amount
    brief_hash: Digest
    delivery_hash: Digest | None
    deadline_ns: Timestamp
    status: Literal["funded", "delivered", "paying", "paid", "refunding", "refunded"]

    @model_validator(mode="after")
    def bounds(self):
        if not 0 < int(self.amount) < 2**128 or int(self.deadline_ns) >= 2**64:
            raise ValueError("Invalid job amounts or deadline")
        if self.status in {"delivered", "paying", "paid"} and self.delivery_hash is None:
            raise ValueError("Delivery digest required")
        return self


class NearUnavailable(Exception):
    """A sanitized, retryable upstream read error."""


class NearReader:
    def __init__(self, contract_id: str, *, transport=None):
        if (
            not re.fullmatch(ACCOUNT, contract_id)
            or len(contract_id) > 64
            or not contract_id.endswith(".testnet")
        ):
            raise ValueError("REELOS_NEAR_CONTRACT_ID must be a named .testnet account")
        self.contract_id = contract_id
        self.transport = transport

    def view(self, method: str, args: dict, schema):
        payload = {
            "jsonrpc": "2.0",
            "id": "reelos",
            "method": "query",
            "params": {
                "request_type": "call_function",
                "finality": "final",
                "account_id": self.contract_id,
                "method_name": method,
                "args_base64": base64.b64encode(json.dumps(args).encode()).decode(),
            },
        }
        try:
            with httpx.Client(
                timeout=10, transport=self.transport, follow_redirects=False
            ) as client:
                response = client.post(TESTNET_RPC, json=payload)
                response.raise_for_status()
            if len(response.content) > 65536:
                raise ValueError("Oversized response")
            envelope = response.json()
            if envelope.get("error"):
                raise ValueError("RPC error")
            result = envelope["result"]
            height, block_hash, raw = result["block_height"], result["block_hash"], result["result"]
            if (
                type(height) is not int
                or height <= 0
                or not isinstance(block_hash, str)
                or not block_hash
                or not isinstance(raw, list)
                or any(type(x) is not int or not 0 <= x <= 255 for x in raw)
            ):
                raise ValueError("Invalid RPC result")
            value = TypeAdapter(schema).validate_python(json.loads(bytes(raw)))
        except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
            raise NearUnavailable("Unable to read finalized NEAR state. Try again.") from None
        return value, {
            "network": "testnet",
            "contract_id": self.contract_id,
            "block_height": height,
            "block_hash": block_hash,
        }

    def get_config(self):
        value, block = self.view("get_config", {}, ChainConfig)
        return block | {"enabled": True, "config": value.model_dump()}

    def get_job(self, job_id: str):
        if not re.fullmatch(r"[a-f0-9]{32}", job_id):
            raise ValueError("Invalid job id")
        value, block = self.view("get_job", {"job_id": job_id}, ChainJob | None)
        return block | {"job": value.model_dump() if value else None}
