# ReelOS editing escrow

First NEAR increment for ReelOS Studio. This contract has not been deployed.
It holds a fixed editing price until the client approves a provider-delivered preview.
After the deadline, the client can recover the editing price, including when a
preview was delivered but not approved. The separate 0.02 NEAR storage fee is retained.
This is client-approved payment, not automated quality arbitration or copyright protection.

## Build and test

Use an official Rust toolchain (1.92.0 was used for the Wasm build), with
`wasm32-unknown-unknown` installed. Homebrew-built rustc may be incompatible with
the official target libraries; use a matching compiler and standard library.

```sh
cargo test --manifest-path contracts/reelos-escrow/Cargo.toml --locked
cargo fmt --manifest-path contracts/reelos-escrow/Cargo.toml -- --check
cargo clippy --manifest-path contracts/reelos-escrow/Cargo.toml --all-targets --locked -- -D warnings
cargo build --manifest-path contracts/reelos-escrow/Cargo.toml --target wasm32-unknown-unknown --release --locked
```

Output: `target/wasm32-unknown-unknown/release/reelos_escrow.wasm` in this directory.
Lockfile is checked in; SDK 5.24.1 supports the installed Rust compiler.

## Methods

| Method | Caller / attached deposit | Result |
| --- | --- | --- |
| `new(provider, price)` | Contract account, during initialization | Sets immutable studio and price |
| `get_config()` | Anyone, view | Provider, price and storage fee |
| `get_job(job_id)` | Anyone, view | Job or null |
| `fund_job(job_id, brief_hash, deadline_ns)` | Client; exact price + storage fee | Funded job |
| `deliver_job(job_id, delivery_hash)` | Provider; none | Delivered job |
| `approve_job(job_id)` | Funding client; none | Payout, then callback finalization |
| `refund_job(job_id)` | Funding client after deadline; none | Refund, then callback finalization |
| `on_transfer(job_id)` | Private callback; never called by browser | Final status or restored retryable status |

Amounts are integer yoctoNEAR strings, timestamps are nanosecond strings.
IDs are 32 lowercase hex characters; hashes are 64 lowercase hex characters.
Funding deadline must be between one hour and seven days ahead.
Delivery and approval must occur strictly before that deadline.
The onchain state never contains videos, editing instructions or preview URLs.

Deploy to a funded dedicated testnet contract account, with a separate testnet
provider account, and initialize atomically with deployment. No deployment or
wallet signing is performed by the test suite. The deployer retains any account
keys; this prototype is not represented as an immutable or audited escrow.

## Verification limits and next integration

SDK mocked-VM tests cover permissions, lifecycle, storage charging and callback
recovery. They do not execute real network receipts. A deployed testnet rehearsal
must verify transfers, callback gas and balances before claiming end-to-end support.
The wallet UI and ReelOS worker are not connected to this contract yet.

Contract design sources: [NEAR state](https://docs.near.org/smart-contracts/anatomy/storage),
[transfers](https://docs.near.org/smart-contracts/anatomy/actions),
[SDK](https://docs.rs/near-sdk/5.24.1/near_sdk/).

## Local build on this machine

The matching official compiler and standard libraries are installed in an isolated
folder. With the existing Homebrew Cargo, the verified build command is:

```sh
RUSTC="$HOME/.local/share/reelos-rust-wasm-1.92.0/bin/rustc" cargo build --manifest-path contracts/reelos-escrow/Cargo.toml --target wasm32-unknown-unknown --release --locked
```

Validation: 26 contract tests, format and Clippy passed; release Wasm built. The
existing editor's 205 backend tests passed using `uv --directory backend run python -m pytest -q`.
Use `python -m pytest` in this copied workspace: copied executable shebangs can
otherwise invoke the original workspace's interpreter. No paid model calls were made.
