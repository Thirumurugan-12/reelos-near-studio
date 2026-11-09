#!/usr/bin/env bash
# Prerequisite: scripts/verify.sh app. Leaves its generated media in the printed temp directory.
set -euo pipefail
cd "$(dirname "$0")/.."
review_data="$(mktemp -d "${TMPDIR:-/tmp}/reelos-review.XXXXXX")"
uv --directory backend run python scripts/reviewer_demo.py seed "$review_data"
project_id="$(uv --directory backend run python -c 'import json,sys; print(json.load(open(sys.argv[1]))["project_id"])' "$review_data/reviewer-demo.json")"
uv --directory backend run python scripts/reviewer_demo.py serve "$review_data" > "$review_data/backend.log" 2>&1 &
backend_pid=$!
cleanup() { kill "$backend_pid" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
printf '\nGenerated demo: http://127.0.0.1:3102/?project=%s\nArtifacts and backend log: %s\nNo AI calls or wallet transactions. Ctrl+C stops the demo.\n\n' "$project_id" "$review_data"
MODEL_API_KEY='' REELOS_API_BUDGET_USD=0 BACKEND_URL=http://127.0.0.1:8102 NEXT_TELEMETRY_DISABLED=1 npm --prefix frontend run dev -- --port 3102
