# Build checklist

- [x] Escrow contract: funding, provider delivery, client approval and deadline refunds.
  Verified: 26 SDK tests, fmt, clippy and release Wasm build; includes transfer-failure recovery.
  Existing editor: 205 backend tests passed using the copied project interpreter.
  Live testnet transfers remain part of the final rehearsal.
- [x] Testnet read adapter: verify onchain state without trusting a browser payment claim.
  Verified: RPC boundary tests, malformed responses and testnet-only configuration.
  Configure a deployed testnet contract before live reads; see ../docs/NEAR_SETUP.md.
- [x] Wallet UI implementation: fund, inspect, approve and refund jobs; show costs before signing.
  Verified: typecheck, production build, 12 frontend tests and real-browser layout/recovery checks.
  Actual Meteor signatures and live receipts remain in the testnet rehearsal below.
- [x] Worker integration implementation: one paid job maps to one persisted render, with delivery digest.
  Verified: finalized-payment boundary, concurrent starts dispatch once, failed work is not replayed,
  and a real generated-video export with mocked model calls. Provider publishes delivery from wallet.
- [ ] Testnet rehearsal and demo: actual receipts and one complete funded edit.
  Verify: fresh clone README, independent wallet and published demo review.
