# Build checklist

- [x] Escrow contract: funding, provider delivery, client approval and deadline refunds.
  Verified: 26 SDK tests, fmt, clippy and release Wasm build; includes transfer-failure recovery.
  Existing editor: 205 backend tests passed using the copied project interpreter.
  Live testnet transfers remain part of the final rehearsal.
- [x] Testnet read adapter: verify onchain state without trusting a browser payment claim.
  Verified: RPC boundary tests, malformed responses and testnet-only configuration.
  Configure a deployed testnet contract before live reads; see ../docs/NEAR_SETUP.md.
- [ ] Wallet UI: fund, inspect, approve and refund jobs; show costs before signing.
  Verify: typecheck, build and real-browser wallet flow.
- [ ] Worker integration: one paid job maps to one persisted render, with delivery digest.
  Verify: mocked model execution, repeat requests and restart recovery.
- [ ] Testnet rehearsal and demo: actual receipts and one complete funded edit.
  Verify: fresh clone README, independent wallet and published demo review.
