# Compiled-Wasm escrow rehearsal

```sh
npm --prefix contracts/sandbox ci --ignore-scripts
npm --prefix contracts/sandbox test
```

Build the contract first using the command in ../reelos-escrow/README.md.
The launcher downloads the official NEAR Sandbox runtime **2.14.0-rc.5** to a user-local
cache, matching testnet protocol 88 checked on 9 November 2026. It verifies the
runtime version before running. Apple Silicon macOS and Linux x64 are supported.
The older runtime bundled with near-workspaces (2.6.2 / protocol 77) rejects the
Rust 1.92 artifact; the test deliberately does not silently use it.

No public chain is used. Accounts, signatures, gas and balances are local Sandbox
fixtures. The test verifies the parent-signed create/fund/deploy/initialize batch
for a keyless escrow, then funding, unauthorized delivery rejection, early refund
rejection, delivery, the provider's exact payment, double payment rejection and a
refund after time advances. Transfer callbacks execute in the node.

The provider's earlier delivery gas refund must settle before comparing payment
balances. Without that wait, an unrelated refund contaminates the balance delta.

The tar dependency is overridden to 7.5.22 to fix archive-extraction advisories in
the bundled installer. Remaining dependency audit findings are low severity.
The sandbox runtime is fetched from NEAR's official build.nearprotocol.com bucket.
