"""Command interface to the same running editing service used by the web workspace."""

import argparse
import json
import sys
import time
from pathlib import Path

import httpx


def main():
    parser = argparse.ArgumentParser(prog="reelos")
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("health")
    commands.add_parser("usage")
    commands.add_parser("projects")
    commands.add_parser("effects", help="List all catalog effects, options and preview URLs")
    apply = commands.add_parser("apply", help="Apply a catalog effect as a new edit version")
    apply.add_argument("project")
    apply.add_argument("version")
    apply.add_argument("effect")
    apply.add_argument("--start", type=float, required=True)
    apply.add_argument("--end", type=float, required=True)
    apply.add_argument("--text", default="")
    apply.add_argument("--options-file", type=Path)
    apply.add_argument("--media", nargs="*", default=[])

    create = commands.add_parser("create")
    create.add_argument("name")
    upload = commands.add_parser("upload")
    upload.add_argument("project")
    upload.add_argument("file", type=Path)
    upload.add_argument("--role", choices=["source", "reference", "supporting"], default="source")
    draft = commands.add_parser("draft")
    draft.add_argument("project")
    draft.add_argument("asset")
    draft.add_argument("instruction")
    draft.add_argument("--subject", default="person")
    draft.add_argument("--subject-id")
    draft.add_argument("--reference")
    draft.add_argument("--storyboard-only", action="store_true")
    draft.add_argument(
        "--full-length", action="store_true", help="Edit the entire source without trimming."
    )
    revise = commands.add_parser("revise")
    revise.add_argument("project")
    revise.add_argument("version")
    revise.add_argument("instruction")
    render = commands.add_parser("render")
    render.add_argument("project")
    render.add_argument("version")
    render.add_argument("--quality", choices=["preview", "export"], default="preview")
    job = commands.add_parser("job")
    job.add_argument("project")
    job.add_argument("id")
    job.add_argument("--wait", action="store_true")
    plan = commands.add_parser("plan")
    plan.add_argument("project")
    plan.add_argument("version")
    args = parser.parse_args()
    try:
        with httpx.Client(base_url=args.url.rstrip("/") + "/api/", timeout=180) as client:
            if args.command in {"health", "usage", "projects", "effects"}:
                result = client.get(args.command)
            elif args.command == "apply":
                options = json.loads(args.options_file.read_text()) if args.options_file else {}
                result = client.post(
                    f"projects/{args.project}/effects",
                    json={
                        "version_id": args.version,
                        "start": args.start,
                        "end": args.end,
                        "params": {
                            "fx": args.effect,
                            "text": args.text,
                            "options": options,
                            "media_ids": args.media,
                        },
                    },
                )
            elif args.command == "create":
                result = client.post("projects", json={"name": args.name})
            elif args.command == "upload":
                with args.file.open("rb") as file:
                    result = client.post(
                        f"projects/{args.project}/assets",
                        files={"file": file},
                        data={"role": args.role},
                    )
            elif args.command == "job":
                deadline = time.monotonic() + 900
                while True:
                    result = client.get(f"projects/{args.project}/jobs/{args.id}")
                    result.raise_for_status()
                    if not args.wait or result.json()["status"] not in {"queued", "running"}:
                        break
                    if time.monotonic() > deadline:
                        raise ValueError("Wait timed out. The job may still run; check its ID.")
                    time.sleep(1)
            elif args.command == "plan":
                result = client.get(f"projects/{args.project}/versions/{args.version}/plan")
            else:
                data = {"action": args.command}
                if args.command == "draft":
                    data.update(
                        asset_id=args.asset,
                        instruction=args.instruction,
                        subject_prompt=args.subject,
                        subject_id=args.subject_id,
                        reference_id=args.reference,
                        review_storyboard=args.storyboard_only,
                        output_mode="full" if args.full_length else "reel",
                    )
                else:
                    data.update(version_id=args.version)
                    if args.command == "revise":
                        data["instruction"] = args.instruction
                    else:
                        data["quality"] = args.quality
                result = client.post(f"projects/{args.project}/jobs", json=data)
            if result.is_error:
                raise ValueError(result.json().get("error", {}).get("message", "Request failed"))
            print(json.dumps(result.json(), indent=2))
    except (httpx.HTTPError, ValueError, OSError) as exc:
        print(f"ReelOS: {exc}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
