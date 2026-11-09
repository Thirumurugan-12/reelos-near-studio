# NEAR Studio verification — 8 November 2026

Implemented on codex/near-paid-jobs in the separate near-hackathon copy.

## Verified locally

- Backend: 244 pytest tests passed, including 15 paid-order tests.
- Frontend: 12 tests passed; TypeScript and Next.js production build passed.
- Ruff and diff whitespace checks passed.
- Existing escrow: 26 tests and release Wasm build verified in the earlier increment.
- Paid-order tests cover immutable briefs, wrong client/amount/digest/deadline,
  missing funding, changed configuration/source, colliding IDs, cross-project access,
  concurrent starts, and no automatic replay of failed work.
- The generated-footage test runs the real renderer, serves an MP4 export and
  computes its SHA-256; Meta model responses and chain state are test doubles.
  It asserts that no paid model calls are reserved.
- Browser verification used an isolated local fixture for the funded receipt and
  generated-video preview. Video readyState=4, correct price + storage breakdown,
  and saved-order reopen/recovery were verified. No wallet was signed in or used.
- Browser width checks: 320, 768, 1024 and 1440; no horizontal document overflow.
- Actual undeployed configuration shows disabled payment/signing controls and
  the copied project's available source projects. Browser warning/error logs empty.
- Wallet SDK high advisories fixed by the recorded dependency overrides.
  14 low advisories remain through the upstream elliptic/secp256k1 dependency chain.

## Still required

- Fund dedicated testnet accounts, deploy and initialize escrow, configure its ID.
- Complete real Meteor connect/reject/switch/sign flows on the deployed contract.
- Exercise live transfer/callback outcomes, provider delivery and client approval/refund.
- Rehearse a real Meta model edit with an intentional small budget and usable credentials.
- Review multi-subject recovery: paid drafts are deliberately not replayed automatically.
- Prepare the public repository and new hackathon demo; neither has been published.

## Preview

Frontend: http://127.0.0.1:3101/orders; backend: http://127.0.0.1:8101.
The preview uses this copy's data directory and a zero API budget. The generated
browser fixture server was stopped and is not part of application code.

# 9 November 2026 — full runtime rehearsal and wallet deployment preparation

- Verified 11 testnet NEAR total on the user's public studio account before testing.
- 28 contract unit tests and 249 backend tests pass; 15 frontend tests pass.
- Release Wasm rebuilt (259,337 bytes); Clippy, Ruff, typecheck and production build pass.
- Full compiled-Wasm Sandbox rehearsal passes on nearcore 2.14.0-rc.5 / protocol 88,
  matching the public testnet runtime. Includes real local receipts and callbacks,
  exact payment, deadline refund, duplicate/unauthorized action rejection and a
  parent-signed atomic deployment into a new keyless subaccount.
- Default workspaces runtime 2.6.2 / protocol 77 rejected the modern artifact. The
  reproducible launcher now pins the matching runtime instead of relying on that default.
- `/setup` reviews a 3 testnet NEAR deployment and requires a wallet connection,
  explicit acknowledgement and Meteor signature. No private key is imported.
- Activation verifies finalized config, deployed code SHA-256 and no access keys,
  then sets only REELOS_NEAR_CONTRACT_ID in the local ignored environment file.
- Tests ensure activation cannot accept mainnet, wrong pricing/provider, altered
  code or an escrow with access keys; existing environment credentials are preserved.
- Found a generated-key console diagnostic in pinned Meteor SDK 1.0.24 before any
  wallet connection. An explicit pre-bundle patch removes that line. The guard is
  repeatable and rejects dependency-version changes; a regression test covers it.
- Browser checks: setup terms and disabled deployment before consent, desktop and
  320px layout, no console errors/warnings before wallet connection.
- The local server explicitly allows the preview's 3101 origin for POST requests.
- No public wallet signature, public deployment, or paid model call has occurred.
  The next step requires the user's wallet connection/signature on `/setup`.

## 9 November — Meteor restriction resolved with official CLI

- User's screenshot confirmed Meteor rejects app-initiated DeployContract. Removed
  the transaction builder and replaced setup with CLI guidance and read-only verification.
- Official near-cli-rs 0.31.1 sponsor service created `reelos-escrow-20261109.testnet`
  with 10 testnet NEAR and a fresh local deployment key. No studio credentials used.
- Public deployment and private self-initialization succeeded atomically:
  `HehvqR2nvW6aD2QJPu23AEDp5EWeAhjZav9MXVWznuSh`.
- Finalized RPC confirms provider `thirumurugan12.testnet`, price 0.1 NEAR,
  storage fee 0.02 NEAR and matching compiled Wasm SHA-256
  `20d265c2c5217c81d00073a019825fd16a675c57e8fb7f72ab72aab517e745d6`.
- One full-access deployment key remains in the local CLI credential store, outside
  the repository with restricted permissions. The testnet escrow is upgradeable.
- Activation now accepts a separate named testnet contract with explicit acknowledgement
  of retained developer keys. Default derived keyless activation still rejects keys.
- Public wallet funding/delivery/approval and real paid-model editing remain pending.
- Local activation succeeded and persisted only REELOS_NEAR_CONTRACT_ID. Browser
  verifies live 0.1 + 0.02 = 0.12 NEAR pricing with Meteor connection available.
- Regression checks: 251 backend tests, 13 frontend tests, TypeScript, production
  build and Ruff pass. Setup no longer has a wallet deployment/signing control.
