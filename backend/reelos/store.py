"""Local durable state. SQLite transactions serialize budget claims across processes."""

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from reelos.pricing import PRICING_AS_OF, PRICING_SOURCE, estimate_cost


def new_id() -> str:
    return uuid.uuid4().hex


class Store:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = self.root / "reelos.sqlite"
        with self.connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS records "
                "(kind TEXT, id TEXT, project_id TEXT, payload TEXT, "
                "PRIMARY KEY(kind,id))"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS api_calls "
                "(id TEXT PRIMARY KEY, model TEXT, reserve REAL, status TEXT, "
                "usage TEXT, latency REAL, created REAL)"
            )

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.db, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def put(self, kind: str, id: str, data: dict) -> dict:
        value = data | {"id": id}
        with self.connect() as db:
            db.execute(
                "INSERT OR REPLACE INTO records VALUES (?,?,?,?)",
                (kind, id, data.get("project_id", id), json.dumps(value)),
            )
        return value

    def get(self, kind: str, id: str, project_id: str | None = None) -> dict:
        with self.connect() as db:
            row = db.execute(
                "SELECT payload,project_id FROM records WHERE kind=? AND id=?", (kind, id)
            ).fetchone()
        if not row or (project_id and row["project_id"] != project_id):
            raise KeyError("Resource not found")
        return json.loads(row["payload"])

    def list(self, kind: str, project_id: str | None = None) -> list[dict]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT payload FROM records WHERE kind=? "
                "AND (? IS NULL OR project_id=?) ORDER BY rowid DESC LIMIT 200",
                (kind, project_id, project_id),
            ).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def reserve(self, model: str, amount: float, limit: float) -> str:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            total = db.execute("SELECT COALESCE(SUM(reserve),0) FROM api_calls").fetchone()[0]
            if amount <= 0 or total + amount > limit:
                raise ValueError("Local API budget reservation limit reached.")
            id = new_id()
            db.execute(
                "INSERT INTO api_calls VALUES (?,?,?,?,?,?,?)",
                (id, model, amount, "pending", "{}", 0, time.time()),
            )
        return id

    def finish_call(self, id: str, status: str, usage: dict, latency: float):
        with self.connect() as db:
            db.execute(
                "UPDATE api_calls SET status=?,usage=?,latency=? WHERE id=?",
                (status, json.dumps(usage), latency, id),
            )

    def budget(self) -> dict:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM api_calls ORDER BY created DESC").fetchall()
        estimates = [estimate_cost(r["model"], json.loads(r["usage"])) for r in rows]
        return {
            "reserved_usd": sum(r["reserve"] for r in rows),
            "estimated_known_usd": round(sum(v for v in estimates if v is not None), 8),
            "unpriced_calls": sum(v is None for v in estimates),
            "pricing_as_of": PRICING_AS_OF,
            "pricing_source": PRICING_SOURCE,
            "calls": [
                {
                    "id": r["id"],
                    "model": r["model"],
                    "status": r["status"],
                    "latency": r["latency"],
                    "usage": json.loads(r["usage"]),
                    "reserved_usd": r["reserve"],
                    "estimated_usd": estimate,
                }
                for r, estimate in zip(rows, estimates, strict=True)
            ],
        }
