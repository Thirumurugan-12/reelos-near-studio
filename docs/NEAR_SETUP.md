# NEAR testnet setup

The editor and contract tests can be developed without wallet accounts.
Keep real credentials in the ignored `.env`; never paste seed phrases or private keys into chat.

## Owner setup

MyNearWallet no longer creates new accounts. Use [Meteor Wallet](https://wallet.meteorwallet.app/).
Verified on 8 November 2026: the new-user page opens on “Create a Password” and defaults
to Mainnet. Open the network badge at the top right of the setup card and choose
**Testnet** before proceeding. Set the password and complete the remaining wallet
creation steps yourself. Share only the resulting public testnet account ID.
Keep the recovery information in your own wallet. Only the public account ID is needed here.
The studio provider, contract deployment account and demo customer will be separate identities
for the end-to-end rehearsal. Choose actual available names at setup time.
No mainnet funding, ETH transfer or token purchase is needed for this testnet prototype.

MetaMask has a [NEAR Snap](https://snaps.metamask.io/snap/npm/near-snap/plugin/)
that advertises testnet support. It has not been tested with this app; the initial
wallet integration will target a native NEAR testnet wallet.

Working defaults: ReelOS Studio, price 0.1 testnet NEAR, deadline 24 hours.
Contract storage costs an additional 0.02 testnet NEAR; gas is separate.
Price is fixed on contract initialization, and the application reads it from chain.

## Read adapter

Leave `REELOS_NEAR_CONTRACT_ID` blank until the contract is actually deployed.
Set it to the deployed named `.testnet` account in `.env`, then restart the backend.

- `GET /api/near/config`: disabled configuration, or finalized onchain price/provider.
- `GET /api/near/jobs/{job_id}`: finalized job plus block height and block hash.
- Missing job: 404. Not configured: 503. Chain or malformed response: 502.
- This adapter has no private key, signing method or browser-supplied payment status.
- New routes are part of the existing controlled single-user local deployment.

[NEAR RPC reference](https://docs.near.org/api/rpc/contracts)
[NEAR CLI account creation](https://docs.near.org/tools/cli#account)

## Local paid studio

Open `/orders` (or “Paid studio” in the editor header). Choose a project and source
video, write the brief, connect Meteor on testnet, then review the order. No funds
move until the funding action. After finalized funding, Start AI editing verifies
the brief/client/amount/deadline and dispatches one draft/export. The provider
connects their account to publish the rendered file digest; the client reconnects
to approve payment or refund after the deadline. Saved orders allow returning
after reload or switching wallets. A local preview is visible before approval;
escrow does not prevent copying footage.

Paid editing stays disabled when the contract is unset. Do not set the contract
ID to the provider's empty wallet account; it must hold the initialized escrow Wasm.

To avoid the original editor's ports, start this copy in two terminals:

```sh
REELOS_API_BUDGET_USD=0 uv --directory backend run python -m uvicorn reelos.api:create_app --factory --host 127.0.0.1 --port 8101
BACKEND_URL=http://127.0.0.1:8101 npm --prefix frontend run dev -- --port 3101
```

The zero API budget prevents paid model calls during UI review. Set an intentional
small budget when rehearsing a real edit with the studio's working Meta credentials.

SDKs: wallet-selector core and Meteor 10.1.4, loaded only when connecting.
Transitive overrides pin nanoid 5.1.16 and decode-uri-component 0.5.1 to fix high
severity advisories. The dependency audit retains low-severity elliptic/secp256k1
findings inherited through the NEAR SDK; no unreviewed major downgrade was applied.
Sources: [Meteor adapter](https://github.com/near/wallet-selector/tree/main/packages/meteor-wallet),
[wallet selector](https://github.com/near/wallet-selector/tree/main/packages/core).

## Wallet-signed keyless deployment

Open `/setup` in the local preview. Connect the studio's named testnet account,
review the exact `escrow.<studio-account>` destination, acknowledge that the contract
account is permanent, then review the transaction in Meteor. It transfers **3
testnet NEAR** (plus gas) to cover contract code/state storage. The account is
created, funded, deployed and initialized in one atomic batch with **no access keys**.
The studio wallet's private key never reaches this app. The deployment account has
no upgrade/delete/withdraw mechanism; its setup balance cannot be reclaimed.

The initializer `new_for_studio` derives the provider from predecessor identity
and only accepts the exact `escrow.<predecessor>` account. The existing private
self-initializer is retained for independently keyed deployments and tests.

After signing, the page verifies finalized contract settings, exact compiled code
hash and an empty access-key list before enabling the paid studio. If the request
times out after signing, use Verify an existing deployment before retrying.
The activation endpoint changes only the local copied project's ignored environment.

For the 3101 preview, include the exact Origin allowance when starting the backend:

```sh
REELOS_ALLOWED_ORIGINS=http://127.0.0.1:3101,http://localhost:3101 REELOS_API_BUDGET_USD=0 uv --directory backend run python -m uvicorn reelos.api:create_app --factory --host 127.0.0.1 --port 8101
```

`npm run dev` and `npm run build` explicitly run the pinned Meteor SDK logging
patch even when npm lifecycle scripts are disabled by `.npmrc`. Do not bypass
those scripts when bundling the application.
