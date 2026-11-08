"""Immutable editing briefs and a single render dispatch per finalized payment."""

import hashlib
import json
import time
from typing import Literal

from fastapi.responses import JSONResponse
from pydantic import Field

from reelos.near import Account
from reelos.timeline import Contract, Identifier


class OrderInput(Contract):
    id: Identifier
    client: Account
    asset_id: Identifier
    instruction: str = Field(min_length=1, max_length=2000)
    subject_prompt: str = Field(default="person", min_length=1, max_length=120)
    output_mode: Literal["reel", "full"] = "reel"


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def create_order(editor, reader, pid, data):
    editor.store.get("project", pid)
    asset = editor.store.get("asset", data.asset_id, pid)
    if asset["role"] != "source":
        raise ValueError("Choose source footage for this editing job.")
    request = data.model_dump()
    source_hash = digest(editor.asset_dir(data.asset_id) / "source.mp4")
    config = reader.get_config()
    with editor.store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        existing = db.execute(
            "SELECT payload FROM records WHERE kind='order' AND id=?", (data.id,)
        ).fetchone()
        if existing:
            order = json.loads(existing[0])
            if (
                order["project_id"] != pid
                or order["request"] != request
                or order["source_hash"] != source_hash
            ):
                raise ValueError(
                    "This order ID already belongs to another brief. Create a new order."
                )
            return order
        if db.execute("SELECT 1 FROM records WHERE kind='job' AND id=?", (data.id,)).fetchone():
            raise ValueError("This order ID is already used. Create a new order.")
        deadline = str(time.time_ns() + 24 * 3600 * 10**9)
        brief = {
            "schema": "reelos-order-v1",
            "project_id": pid,
            "source_hash": source_hash,
            "request": request,
            "deadline_ns": deadline,
            "contract_id": config["contract_id"],
            "config": config["config"],
        }
        order = brief | {
            "id": data.id,
            "created_at": time.time(),
            "brief_hash": hashlib.sha256(
                json.dumps(brief, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
        }
        db.execute("INSERT INTO records VALUES ('order',?,?,?)", (data.id, pid, json.dumps(order)))
    return order


def start_order(editor, reader, pid, id):
    order = editor.store.get("order", id, pid)
    # A persisted dispatch is never automatically repeated, even after a timeout/restart.
    try:
        existing = editor.store.get("job", id, pid)
        if existing.get("order_id") != id:
            raise ValueError("This render does not belong to the paid order.")
        return existing
    except KeyError:
        pass
    chain = reader.get_job(id)["job"]
    expected = {
        "client": order["request"]["client"],
        "amount": order["config"]["price"],
        "brief_hash": order["brief_hash"],
        "deadline_ns": order["deadline_ns"],
        "status": "funded",
    }
    if not chain or any(chain.get(k) != v for k, v in expected.items()):
        raise ValueError("The matching editing payment is not confirmed on NEAR yet.")
    config = reader.get_config()
    if config["contract_id"] != order["contract_id"] or config["config"] != order["config"]:
        raise ValueError("Studio configuration changed. Do not fund this order.")
    if int(order["deadline_ns"]) <= time.time_ns():
        raise ValueError("This editing deadline has passed. Use the refund action.")
    if (
        digest(editor.asset_dir(order["request"]["asset_id"]) / "source.mp4")
        != order["source_hash"]
    ):
        raise ValueError("Source footage changed. Do not reuse this editing payment.")
    request = {k: v for k, v in order["request"].items() if k not in {"id", "client"}}
    request.update(action="draft", quality="export")
    job = {
        "id": id,
        "order_id": id,
        "project_id": pid,
        "request": request,
        "status": "queued",
        "stage": "Waiting to start",
        "progress": None,
        "created_at": time.time(),
    }
    with editor.store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        existing = db.execute(
            "SELECT payload FROM records WHERE kind='job' AND id=?", (id,)
        ).fetchone()
        if existing:
            existing_job = json.loads(existing[0])
            if existing_job.get("order_id") != id or existing_job["project_id"] != pid:
                raise ValueError("This render does not belong to the paid order.")
            return existing_job
        running = db.execute(
            "SELECT payload FROM records WHERE kind='job' AND project_id=?", (pid,)
        ).fetchall()
        if any(json.loads(row[0])["status"] in {"queued", "running"} for row in running):
            raise ValueError("This project already has a job running. Wait for it to finish.")
        db.execute("INSERT INTO records VALUES ('job',?,?,?)", (id, pid, json.dumps(job)))
    editor.worker.submit(editor.run, job)
    return job


def order_view(editor, pid, id):
    order = editor.store.get("order", id, pid)
    try:
        job = editor.store.get("job", id, pid)
    except KeyError:
        job = None
    result = order | {"render": job, "delivery_hash": None, "preview_url": None}
    if job and job["status"] == "completed" and job.get("version_id"):
        vid = job["version_id"]
        version = editor.store.get("version", vid, pid)
        quality = "export" if version.get("has_export") else "preview"
        target = editor.version_dir(vid) / f"{quality}.mp4"
        if target.is_file():
            result["delivery_hash"] = digest(target)
            result["preview_url"] = f"/api/projects/{pid}/versions/{vid}/{quality}"
    return result


def mount_orders(app, editor):
    def disabled():
        return JSONResponse(
            {
                "error": {
                    "code": "NEAR_NOT_CONFIGURED",
                    "message": "Paid editing opens after the testnet contract is deployed.",
                }
            },
            503,
        )

    @app.get("/api/projects/{project_id}/orders")
    def list_orders(project_id: Identifier):
        editor.store.get("project", project_id)
        return [
            {
                "id": o["id"],
                "created_at": o["created_at"],
                "instruction": o["request"]["instruction"][:80],
            }
            for o in editor.store.list("order", project_id)
        ]

    @app.post("/api/projects/{project_id}/orders", status_code=201)
    def create(project_id: Identifier, data: OrderInput):
        if app.state.near_reader is None:
            return disabled()
        return create_order(editor, app.state.near_reader, project_id, data)

    @app.get("/api/projects/{project_id}/orders/{order_id}")
    def get(project_id: Identifier, order_id: Identifier):
        return order_view(editor, project_id, order_id)

    @app.post("/api/projects/{project_id}/orders/{order_id}/start")
    def start(project_id: Identifier, order_id: Identifier):
        if app.state.near_reader is None:
            return disabled()
        return start_order(editor, app.state.near_reader, project_id, order_id)
