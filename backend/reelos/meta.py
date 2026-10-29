"""Small server-side Meta Responses client; never retries ambiguous paid requests."""

import time
from pathlib import Path

import httpx

from reelos.config import Settings
from reelos.store import Store


class MetaClient:
    def __init__(self, settings: Settings, store: Store):
        self.settings = settings
        self.store = store

    def upload(self, path: Path) -> str:
        if not self.settings.api_key:
            raise ValueError("Configure MODEL_API_KEY in the server's .env first.")
        with path.open("rb") as file, httpx.Client(timeout=90) as client:
            result = client.post(
                "https://api.meta.ai/v1/files",
                headers={"Authorization": f"Bearer {self.settings.api_key}"},
                data={"purpose": "user_data"},
                files={"file": (path.name, file, "video/mp4")},
            )
        if result.is_error:
            raise ValueError(f"Meta media upload failed (HTTP {result.status_code}).")
        id = result.json().get("id")
        if not isinstance(id, str) or not id.startswith("file-"):
            raise ValueError("Meta returned an invalid media reference.")
        return id

    def response(self, model: str, content: list[dict], **kwargs) -> dict:
        if not self.settings.api_key:
            raise ValueError("Configure MODEL_API_KEY in the server's .env first.")
        call = self.store.reserve(model, self.settings.reserve_usd, self.settings.budget_usd)
        started = time.monotonic()
        recorded = False
        try:
            with httpx.Client(timeout=httpx.Timeout(180, connect=20)) as client:
                response = client.post(
                    "https://api.meta.ai/v1/responses",
                    headers={"Authorization": f"Bearer {self.settings.api_key}"},
                    json={
                        "model": model,
                        "input": [{"type": "message", "role": "user", "content": content}],
                        **kwargs,
                    },
                )
                if response.is_error:
                    raise ValueError(
                        f"Meta request failed (HTTP {response.status_code}). "
                        "Check model access and account limits."
                    )
                data = response.json()
                if data.get("status") not in (None, "completed"):
                    self.store.finish_call(
                        call, "incomplete", data.get("usage", {}), time.monotonic() - started
                    )
                    recorded = True
                    reason = data.get("incomplete_details", {}).get("reason")
                    reason = (
                        reason if reason in {"max_output_tokens", "content_filter"} else "unknown"
                    )
                    raise ValueError(f"Meta response incomplete ({reason}); no edit was applied.")
            self.store.finish_call(
                call, "completed", data.get("usage", {}), time.monotonic() - started
            )
            return data
        except Exception:
            if not recorded:
                self.store.finish_call(call, "failed_or_unknown", {}, time.monotonic() - started)
            raise


def output_text(data: dict) -> str:
    return "".join(
        part.get("text", "")
        for item in data.get("output", [])
        for part in item.get("content", [])
        if part.get("type") == "output_text"
    )
