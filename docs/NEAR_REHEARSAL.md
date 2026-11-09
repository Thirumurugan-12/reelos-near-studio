# Public testnet settlement rehearsal

This bounded rehearsal settles an already-rendered 20s sample. It demonstrates
actual native funding, provider delivery and customer-approved native settlement.
It does not claim a new AI inference or payment-triggered worker render.

Contract: `reelos-escrow-20261109.testnet`.
Provider: `thirumurugan12.testnet`.
Customer: `reelos-demo-client-20261109.testnet`.
Job: `3461ba8334eb447ea57c62cc0a173392`.
Export SHA-256: `bd76a5276856a7306cc4703d0f9c61d31d6ddb4f00ab878b87f70f83772cb0ca`.
[Funding receipt](https://explorer.testnet.near.org/transactions/6JSmQc96HwwMYYF8WnfDmvj5Vr9hphPqa1qsjqFPS1Hc).

Anyone can inspect the current chain state without keys:

```sh
near contract call-function as-read-only reelos-escrow-20261109.testnet get_job json-args '{"job_id":"3461ba8334eb447ea57c62cc0a173392"}' network-config testnet now
```

Locally, `/rehearsal` reads an ignored manifest and verifies the actual MP4 digest
plus finalized chain data. The provider connects Meteor and signs `deliver_job`
with zero attached NEAR, plus network gas. A separate customer must then sign
`approve_job` to release exactly the 0.1 NEAR price; 0.02 remains for storage.
If approval never occurs, the customer can refund the price after the deadline.

The manifest and footage remain outside Git. The page is not a general custody
endpoint: the backend never signs. Test CLI keys stay in a restricted credential
store outside the repository. Use your own funded accounts to repeat this on a
new contract, or run the compiled-Wasm Sandbox scenario without public funds.
## Completed public receipts — 9 November 2026

| Step | Signer | Finalized receipt |
| --- | --- | --- |
| Fund 0.12 NEAR | `reelos-demo-client-20261109.testnet` | [6JSmQc96…](https://explorer.testnet.near.org/transactions/6JSmQc96HwwMYYF8WnfDmvj5Vr9hphPqa1qsjqFPS1Hc) |
| Publish export digest | `thirumurugan12.testnet` via Meteor | [CT4YtFQm…](https://explorer.testnet.near.org/transactions/CT4YtFQmSN29ZGqHTGT4Wqa2f8UxZih9GXvNxqKT2c5E) |
| Approve and release | Separate demo customer | [AKZdntwS…](https://explorer.testnet.near.org/transactions/AKZdntwS8Y7eEKwHDBoAcNgNaPCwgbfEvUsxsBpMvKwA) |

The approval's `EXPERIMENTAL_tx_status` response was `FINAL` and successful.
Its receipt tree contains a successful native `Transfer` of
`100000000000000000000000` yoctoNEAR (0.1 NEAR) to
`thirumurugan12.testnet`, followed by the contract's `transfer_succeeded` log.
The job was read as `paid` at finalized block 276903508. The 0.02 NEAR retained
storage fee is separate from gas; small unused-gas refunds are not the studio payout.

Both customer calls were signed with a dedicated local test-only CLI key. The
provider signed delivery in Meteor. This proves settlement of the existing MP4,
not a newly purchased AI render. The regular paid-worker integration is covered
by local tests; its complete public-testnet render flow remains unverified.

The deprecated `rpc.testnet.near.org` returned HTTP 429 during the rehearsal.
The app now uses the [officially listed FASTNEAR testnet RPC](https://docs.near.org/api/rpc/providers)
for finalized reads and wallet construction; the delivery succeeded after that fix.
