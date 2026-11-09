"""Read-only evidence for a contract settlement rehearsal of an existing export."""

import hashlib
import json
from pathlib import Path
from typing import Literal

from fastapi.responses import FileResponse
from pydantic import ValidationError

from reelos.near import Account, Digest, Timestamp
from reelos.timeline import Contract, Identifier

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/near-demo/payment-rehearsal.json"
OUTPUT = ROOT / "data/near-demo/reelos-test-footage-broll-v2-1080p.mp4"


class Rehearsal(Contract):
    network: Literal["testnet"] = "testnet"
    client: Account
    contract_id: Account
    job_id: Identifier
    brief_hash: Digest
    deadline_ns: Timestamp
    delivery_hash: Digest
    fund_tx: str | None = None
    delivery_tx: str | None = None
    approve_tx: str | None = None


def mount_rehearsal(app):
    @app.get("/api/near/rehearsal")
    def evidence():
        if not MANIFEST.is_file() or not OUTPUT.is_file():
            raise KeyError("Payment rehearsal is not prepared.")
        try:
            spec = Rehearsal.model_validate(json.loads(MANIFEST.read_text()))
        except (OSError, ValueError, ValidationError):
            raise ValueError(
                "The local rehearsal manifest is invalid. Rebuild it before signing."
            ) from None
        reader = app.state.near_reader
        if reader is None or reader.contract_id != spec.contract_id:
            raise ValueError("Rehearsal contract differs from the configured studio.")
        config = reader.get_config()["config"]
        if spec.client == config["provider"] or not spec.client.endswith(".testnet"):
            raise ValueError("The rehearsal requires a separate testnet customer.")
        with OUTPUT.open("rb") as source:
            digest = hashlib.file_digest(source, "sha256").hexdigest()
        if digest != spec.delivery_hash:
            raise ValueError("The output changed after this rehearsal was prepared.")
        state = reader.get_job(spec.job_id)
        job = state["job"]
        expected = {
            "client": spec.client,
            "brief_hash": spec.brief_hash,
            "deadline_ns": spec.deadline_ns,
            "amount": config["price"],
        }
        if job and (
            any(job.get(k) != v for k, v in expected.items())
            or job.get("delivery_hash") not in (None, digest)
        ):
            raise ValueError("The finalized job does not match this rehearsal and export.")
        return spec.model_dump() | {
            "mode": "contract_rehearsal",
            "provider": config["provider"],
            "price": config["price"],
            "storage_fee": config["storage_fee"],
            "total_deposit": str(int(config["price"]) + int(config["storage_fee"])),
            "chain": job,
            "block_height": state["block_height"],
            "block_hash": state["block_hash"],
            "video_url": "/api/near/rehearsal/video",
        }

    @app.get("/api/near/rehearsal/video")
    def video():
        if not OUTPUT.is_file():
            raise KeyError("Demo export is not ready.")
        return FileResponse(OUTPUT, media_type="video/mp4")
