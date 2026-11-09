"""Generate a public-clone sample through the real API and render worker. No AI calls."""

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import uvicorn
from fastapi.testclient import TestClient

from reelos.api import create_app
from reelos.config import Settings
from reelos.media import inspect_media

CONTRACT = "reelos-escrow-20261109.testnet"


def settings(root: Path) -> Settings:
    # Explicit construction never reads .env or inherited provider credentials.
    return Settings(
        data_dir=root, api_key="", budget_usd=0, broll_art="template", near_contract_id=CONTRACT
    )


def video(path: Path, visual: str, tone: int):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            visual,
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency={tone}:duration=4",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(path),
        ],
        check=True,
        timeout=30,
    )


def checked(response, status=200):
    if response.status_code != status:
        raise RuntimeError(f"Demo API returned {response.status_code}: {response.text[:300]}")
    return response.json()


def seed(root: Path) -> dict:
    root = root.resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError("Choose an empty demo directory; existing projects are never overwritten.")
    root.mkdir(parents=True, exist_ok=True)
    video(root / "generated-source.mp4", "color=c=0x183c32:s=360x640:r=30:d=4", 440)
    video(root / "generated-broll.mp4", "testsrc2=s=360x640:r=30:d=4", 880)
    with TestClient(create_app(settings(root))) as client:
        project = checked(
            client.post(
                "/api/projects",
                json={
                    "name": "Generated review sample — local render, no AI call",
                },
            ),
            201,
        )
        pid = project["id"]
        assets = []
        for name, role in (("source", "source"), ("broll", "supporting")):
            with (root / f"generated-{name}.mp4").open("rb") as clip:
                assets.append(
                    checked(
                        client.post(
                            f"/api/projects/{pid}/assets",
                            data={"role": role},
                            files={"file": (f"generated-{name}.mp4", clip, "video/mp4")},
                        ),
                        201,
                    )
                )
        effect = {"subject_id": "0", "reason": "Deterministic generated review fixture"}
        version = checked(
            client.post(
                f"/api/projects/{pid}/versions",
                json={
                    "plan": {
                        "asset_id": assets[0]["id"],
                        "source_out": 4,
                        "effects": [
                            effect
                            | {
                                "id": "moving-broll",
                                "type": "footage_insert",
                                "start": 1.2,
                                "end": 2.8,
                                "params": {"asset_id": assets[1]["id"], "source_in": 0.2},
                            },
                        ],
                    }
                },
            ),
            201,
        )
        vid = version["id"]
        # Use the normal durable queue and renderer; never fabricate version/job success.
        for quality in ("preview", "export"):
            job = checked(
                client.post(
                    f"/api/projects/{pid}/jobs",
                    json={
                        "action": "render",
                        "version_id": vid,
                        "quality": quality,
                    },
                ),
                202,
            )
            deadline = time.monotonic() + 120
            while job["status"] in {"queued", "running"} and time.monotonic() < deadline:
                time.sleep(0.05)
                job = checked(client.get(f"/api/projects/{pid}/jobs/{job['id']}"))
            if job["status"] != "completed":
                raise RuntimeError(f"Demo render failed: {job.get('error', job['status'])}")
        export_url = f"/api/projects/{pid}/versions/{vid}/export"
        response = client.get(export_url)
        response.raise_for_status()
        assert not client.get("/api/usage").json()["calls"]
        result = {
            "kind": "generated-local-render",
            "project_id": pid,
            "version_id": vid,
            "export_url": export_url,
            "sha256": hashlib.sha256(response.content).hexdigest(),
            "media": inspect_media(root / "versions" / vid / "export.mp4"),
            "model_calls": 0,
            "chain_transactions": 0,
            "note": "Generated local media and a manual timeline; not an AI or paid-chain run.",
        }
        (root / "reviewer-demo.json").write_text(json.dumps(result, indent=2) + "\n")
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("seed", "serve"))
    parser.add_argument("data_dir", type=Path)
    args = parser.parse_args()
    if args.action == "seed":
        print(json.dumps(seed(args.data_dir), indent=2))
    else:
        os.environ["REELOS_ALLOWED_ORIGINS"] = "http://127.0.0.1:3102,http://localhost:3102"
        uvicorn.run(create_app(settings(args.data_dir)), host="127.0.0.1", port=8102)


if __name__ == "__main__":
    main()
