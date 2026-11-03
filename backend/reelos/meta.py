"""Small server-side Meta Responses client; never retries ambiguous paid requests."""

import json
import re
import time
from pathlib import Path
from urllib.parse import quote

import httpx

from reelos.config import Settings
from reelos.store import Store

IMAGE_MODEL = "muse-image-1.0"
IMAGE_RESERVE_USD = 0.02  # list price is $0.01 per generated image; reserve double


class MetaClient:
    def __init__(self, settings: Settings, store: Store):
        self.settings = settings
        self.store = store

    def provider_error(self, response: httpx.Response, call: str | None = None) -> ValueError:
        """Keep actionable provider reasons without copying headers, prompts or credentials."""
        try:
            data = response.json()
            error = data.get("error", {}) if isinstance(data, dict) else {}
            error = error if isinstance(error, dict) else {}
        except ValueError:
            error = {}

        def clean(value, limit):
            text = value if isinstance(value, str) else ""
            if self.settings.api_key:
                text = text.replace(self.settings.api_key, "[REDACTED]")
            text = re.sub(r"LLM_[A-Za-z0-9_.-]+", "[REDACTED]", text)
            return " ".join(text.split())[:limit]

        details = {"http_status": response.status_code}
        for field in ("type", "code"):
            value = clean(error.get(field), 80)
            if re.fullmatch(r"[A-Za-z0-9_.:-]{1,80}", value):
                details[field] = value
        details["message"] = clean(error.get("message"), 240) or "No provider reason was returned."
        if call:
            directory = self.store.root / "responses"
            directory.mkdir(exist_ok=True)
            (directory / f"{call}.error.json").write_text(json.dumps(details))
        code = f", {details['code']}" if details.get("code") else ""
        return ValueError(
            f"Meta request failed (HTTP {response.status_code}{code}): {details['message']}"
        )

    def response_failure(self, code: str, call: str) -> ValueError:
        """Record only a fixed category; transport exceptions can contain secrets."""
        messages = {
            "transport_timeout": "Meta request timed out; its outcome is unknown. "
            "Inspect the existing job before retrying.",
            "transport_error": "Meta connection failed; its outcome is unknown. "
            "Inspect the existing job before retrying.",
            "invalid_json": "Meta returned an unreadable response; its outcome is unknown. "
            "Inspect the existing job before retrying.",
        }
        directory = self.store.root / "responses"
        directory.mkdir(exist_ok=True)
        (directory / f"{call}.error.json").write_text(
            json.dumps({"code": code, "message": messages[code]})
        )
        return ValueError(messages[code])

    def file_available(self, file_id: str) -> bool:
        if not self.settings.api_key:
            raise ValueError("Configure MODEL_API_KEY in the server's .env first.")
        with httpx.Client(timeout=30) as client:
            response = client.get(
                "https://api.meta.ai/v1/files/" + quote(file_id, safe=""),
                headers={"Authorization": f"Bearer {self.settings.api_key}"},
            )
        if response.status_code == 404:
            return False
        if response.is_error:
            raise self.provider_error(response)
        return True

    def transcribe(self, path: Path) -> dict:
        if not self.settings.api_key:
            raise ValueError("Configure MODEL_API_KEY in the server's .env first.")
        model = "muse-voice-transcribe-1.0"
        call = self.store.reserve(model, self.settings.reserve_usd, self.settings.budget_usd)
        started = time.monotonic()
        try:
            import json

            with path.open("rb") as audio, httpx.Client(timeout=180) as client:
                response = client.post(
                    "https://api.meta.ai/v1/asr/transcribe",
                    headers={"Authorization": f"Bearer {self.settings.api_key}"},
                    files={
                        "request": (
                            None,
                            json.dumps(
                                {"model": model, "audioEncoding": "WAV", "mode": "ENDPOINTING"}
                            ),
                            "application/json",
                        ),
                        "audio": ("source.wav", audio, "audio/wav"),
                    },
                )
            if response.is_error:
                raise ValueError(f"Source speech analysis failed (HTTP {response.status_code}).")
            result = response.json()
            if not isinstance(result.get("transcript"), str):
                raise ValueError("Speech analysis returned no usable transcript.")
            self.store.finish_call(
                call,
                "completed",
                {"audio_duration_ms": result.get("audioDurationMs")},
                time.monotonic() - started,
            )
            return result
        except Exception:
            self.store.finish_call(call, "failed_or_unknown", {}, time.monotonic() - started)
            raise

    def upload(self, path: Path) -> str:
        if not self.settings.api_key:
            raise ValueError("Configure MODEL_API_KEY in the server's .env first.")
        try:
            with path.open("rb") as file, httpx.Client(timeout=90) as client:
                result = client.post(
                    "https://api.meta.ai/v1/files",
                    headers={"Authorization": f"Bearer {self.settings.api_key}"},
                    data={"purpose": "user_data"},
                    files={"file": (path.name, file, "video/mp4")},
                )
        except httpx.RequestError as exc:
            # Uploads are free and reserve nothing; the job can simply be started again.
            raise ValueError(
                "Meta media upload did not finish (network). Try again; nothing was charged."
            ) from exc
        if result.is_error:
            raise ValueError(f"Meta media upload failed (HTTP {result.status_code}).")
        id = result.json().get("id")
        if not isinstance(id, str) or not id.startswith("file-"):
            raise ValueError("Meta returned an invalid media reference.")
        return id

    def response(
        self, model: str, content: list[dict], request_timeout: float = 180, **kwargs
    ) -> dict:
        if not self.settings.api_key:
            raise ValueError("Configure MODEL_API_KEY in the server's .env first.")
        call = self.store.reserve(model, self.settings.reserve_usd, self.settings.budget_usd)
        started = time.monotonic()
        recorded = False
        try:
            with httpx.Client(timeout=httpx.Timeout(request_timeout, connect=20)) as client:
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
                    raise self.provider_error(response, call)
                data = response.json()
                # Keep private provider evidence before parsing/validation so a bad
                # timeline can be repaired without repeating a paid model request.
                responses = self.store.root / "responses"
                responses.mkdir(exist_ok=True)
                (responses / f"{call}.json").write_text(json.dumps(data))
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
        except httpx.RequestError as exc:
            self.store.finish_call(call, "failed_or_unknown", {}, time.monotonic() - started)
            code = (
                "transport_timeout"
                if isinstance(exc, httpx.TimeoutException)
                else "transport_error"
            )
            raise self.response_failure(code, call) from None
        except json.JSONDecodeError:
            self.store.finish_call(call, "failed_or_unknown", {}, time.monotonic() - started)
            raise self.response_failure("invalid_json", call) from None
        except Exception:
            if not recorded:
                self.store.finish_call(call, "failed_or_unknown", {}, time.monotonic() - started)
            raise

    def images(
        self,
        prompt: str,
        size: str = "1024x1024",
        references: list[str] | None = None,
        n: int = 1,
        request_timeout: float = 240,
    ) -> list[bytes]:
        """Muse Image generation (or editing when reference images are given), never retried.

        references are base64 data URLs of project media. Built-in web, image search and
        shell tools are switched off so results depend only on the prompt and references.
        """
        import base64

        if not self.settings.api_key:
            raise ValueError("Configure MODEL_API_KEY in the server's .env first.")
        call = self.store.reserve(IMAGE_MODEL, IMAGE_RESERVE_USD * n, self.settings.budget_usd)
        started = time.monotonic()
        body = {
            "model": IMAGE_MODEL,
            "prompt": prompt,
            "n": n,
            "size": size,
            "output_format": "png",
            "response_format": "b64_json",
            "tool_enablement": {
                "enable_image_search": False,
                "enable_web_search": False,
                "enable_shell": False,
            },
        }
        endpoint = "generations"
        if references:
            body["images"] = [{"image_url": url} for url in references[:10]]
            endpoint = "edits"
        try:
            with httpx.Client(timeout=httpx.Timeout(request_timeout, connect=20)) as client:
                response = client.post(
                    f"https://api.meta.ai/v1/images/{endpoint}",
                    headers={"Authorization": f"Bearer {self.settings.api_key}"},
                    json=body,
                )
            if response.is_error:
                self.store.finish_call(call, "failed", {}, time.monotonic() - started)
                if response.status_code == 400 and "content_policy" in response.text:
                    raise ValueError("Muse Image declined this request (content policy).")
                raise ValueError(f"Muse Image request failed (HTTP {response.status_code}).")
            data = response.json()
            images = [base64.b64decode(item["b64_json"]) for item in data.get("data", [])]
            usage = dict(data.get("usage") or {}) | {"images_generated": len(images)}
            self.store.finish_call(call, "completed", usage, time.monotonic() - started)
            if not images:
                raise ValueError("Muse Image returned no image.")
            return images
        except httpx.RequestError:
            self.store.finish_call(call, "failed_or_unknown", {}, time.monotonic() - started)
            raise ValueError("Muse Image request did not finish (network).") from None
        except (KeyError, TypeError, json.JSONDecodeError, base64.binascii.Error):
            self.store.finish_call(call, "failed_or_unknown", {}, time.monotonic() - started)
            raise ValueError("Muse Image returned an unreadable response.") from None


def output_text(data: dict) -> str:
    return "".join(
        part.get("text", "")
        for item in data.get("output", [])
        for part in item.get("content", [])
        if part.get("type") == "output_text"
    )
