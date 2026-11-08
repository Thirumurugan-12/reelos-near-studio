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
