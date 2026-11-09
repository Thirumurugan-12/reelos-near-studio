#!/usr/bin/env bash
# Reproduce local checks without provider credentials, wallets or private media.
set -euo pipefail
cd "$(dirname "$0")/.."
part="${1:-all}"
case "$part" in app|contract|all) ;; *) echo 'Usage: scripts/verify.sh [app|contract|all]' >&2; exit 2;; esac
require() { command -v "$1" >/dev/null || { echo "Install $1 before running this check (see README)." >&2; exit 1; }; }
if [[ "$part" != contract ]]; then
  for tool in uv npm node ffmpeg ffprobe; do require "$tool"; done
  export MODEL_API_KEY='' REELOS_API_BUDGET_USD=0 NEXT_TELEMETRY_DISABLED=1
  uv --directory backend sync --frozen
  npm --prefix backend ci --ignore-scripts
  npm --prefix graphics ci --ignore-scripts
  npm --prefix frontend ci --ignore-scripts
  uv --directory backend run ruff check reelos tests scripts/reviewer_demo.py
  uv --directory backend run python -m pytest -q
  npm --prefix frontend test
  npm --prefix frontend run typecheck
  npm --prefix frontend run build
fi
if [[ "$part" != app ]]; then
  for tool in cargo npm node; do require "$tool"; done
  cargo test --manifest-path contracts/reelos-escrow/Cargo.toml --locked
  cargo fmt --manifest-path contracts/reelos-escrow/Cargo.toml -- --check
  cargo clippy --manifest-path contracts/reelos-escrow/Cargo.toml --all-targets --locked -- -D warnings
  cargo build --manifest-path contracts/reelos-escrow/Cargo.toml --target wasm32-unknown-unknown --release --locked
  npm --prefix contracts/sandbox ci --ignore-scripts
  npm --prefix contracts/sandbox test
fi
printf '\nVerification passed (%s). No public transaction or model call was made.\n' "$part"
