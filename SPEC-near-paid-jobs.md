# ReelOS Studio: paid editing jobs

## Objective and accepted scope
Extend existing ReelOS with client-funded video-editing jobs on NEAR testnet.
The user authorized starting the proposed paid-job workflow on 8 November 2026.
Primary track: Agent Economy; secondary: Autonomous Business once the workflow operates end to end.
No prize prediction. Select all tracks supported by actual demonstrated behavior.

## Baseline and boundaries
Reused baseline: commit 2ddb6d1 (Meta ReelOS editor), disclosed separately from NEAR work.
Branch: codex/near-paid-jobs. Never publish secrets, raw footage or private asset URLs.
No mainnet, submission, external publishing, or paid model calls in initial development.
Retain existing editor behavior and use test fixtures for rendering integration tests.

## Contract interface
One configured studio/provider, fixed native NEAR price, no tokens or cross-chain routing.
Client calls fund_job(job_id, brief_hash, deadline_ns), attaching exact price + storage fee.
job_id is 32 lowercase hexadecimal characters; brief_hash and delivery_hash are SHA-256 hex.
Only provider can deliver_job(job_id, delivery_hash) before the deadline.
Only funding client can approve_job(job_id) after delivery and before deadline.
After deadline, client can refund_job whether undelivered or unapproved.
This client-approval model does not arbitrate creative quality or prevent copying a preview.
Payout/refund enter pending states; private callbacks finalize only after successful transfer.
Failures restore the prior actionable state. Pending/terminal jobs cannot pay twice.
Storage fee is retained (0.02 NEAR per job) even after refund; never paid to provider.
Contract account must be initially funded for code/state storage and gas.
View methods: get_config(), get_job(job_id). Amounts/timestamps serialize as decimal strings.

## Trust boundaries and acceptance
Signer predecessor, not request fields, establishes client/provider identity.
Neither AI output nor the HTTP backend may authorize fund release.
Unauthorized callers, duplicate IDs, invalid hashes, wrong deposits, invalid deadlines,
early refunds, double payouts, and public callback attempts must fail.
Only hashes/identifiers, account IDs, amount and status go onchain; footage stays offchain.

## Plan
1. Escrow: tested contract funding, delivery, approval, refund and callback recovery.
2. Read adapter: testnet-only configuration and read-only RPC views; no server-held signing key.
3. Wallet UI: fund and approve in wallet, display actual chain status and explorer links.
4. Worker: verify funded job, render once, provider-signed delivery hash; handle restart/retries.
5. Rehearse with original sample footage; publish reproducible README and new demo.

## Commands and structure
Contract: contracts/reelos-escrow/{src,tests}; Rust + near-sdk 5.24.1 (Rust 1.86+).
Test: cargo test --manifest-path contracts/reelos-escrow/Cargo.toml --locked
Lint: cargo clippy --manifest-path contracts/reelos-escrow/Cargo.toml --all-targets --locked -- -D warnings
Format: cargo fmt --manifest-path contracts/reelos-escrow/Cargo.toml -- --check
Wasm: cargo build --manifest-path contracts/reelos-escrow/Cargo.toml --target wasm32-unknown-unknown --release --locked
Backend regression: uv --directory backend run pytest -q
Code style: explicit enums, integer yoctoNEAR, bounded inputs, small methods.
Testing: SDK mocked VM for access/receipt/state tests; sandbox/deployed-testnet end-to-end later.
