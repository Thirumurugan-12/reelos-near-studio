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

## CLI deployment and local activation

Meteor blocks `DeployContract` requests from apps, including the atomic child-account
batch originally proposed here. Cancel a blocked request; repeating it does not help.
The setup page no longer requests any wallet deployment transaction.
Use the [official NEAR CLI](https://docs.near.org/tools/cli#deploy) with a separate
developer account. No studio wallet seed or private key is needed.

Create a fresh named testnet deployment account with a locally generated key:

```sh
near account create-account sponsor-by-faucet-service YOUR-ESCROW.testnet autogenerate-new-keypair save-to-keychain network-config testnet create
near contract deploy YOUR-ESCROW.testnet use-file contracts/reelos-escrow/target/wasm32-unknown-unknown/release/reelos_escrow.wasm with-init-call new json-args '{"provider":"YOUR-STUDIO.testnet","price":"100000000000000000000000"}' prepaid-gas '100 Tgas' attached-deposit '0 NEAR' network-config testnet sign-with-keychain send
```

Deploy and initialize atomically, using the contract account itself as signer.
The sponsor service creates accounts; it is separate from near-faucet.io top-ups.
Availability and funding may change. Reserve at least 3 testnet NEAR for code/state.
Keep the generated key in the local credential store outside the repository and
restrict its filesystem permissions. Never print or paste it into chat.
The CLI account retains its full-access key, so its holder can upgrade/delete the
contract. This is an explicit testnet rehearsal trust assumption, not immutable escrow.

Open `/setup`, enter the public provider and deployed contract IDs, acknowledge
retained developer control, and verify. Activation checks finalized provider/pricing,
exact compiled code hash and access keys before changing only the local copied
project's ignored environment setting. Already-configured contracts cannot be
silently switched. The default legacy keyless-subaccount path still rejects any keys.

The `new_for_studio` initializer remains tested for factories/other supported tools;
it is not offered through Meteor.

For the 3101 preview, include the exact Origin allowance when starting the backend:

```sh
REELOS_ALLOWED_ORIGINS=http://127.0.0.1:3101,http://localhost:3101 REELOS_API_BUDGET_USD=0 uv --directory backend run python -m uvicorn reelos.api:create_app --factory --host 127.0.0.1 --port 8101
```

`npm run dev` and `npm run build` explicitly run the pinned Meteor SDK logging
patch even when npm lifecycle scripts are disabled by `.npmrc`. Do not bypass
those scripts when bundling the application.

## Current RPC endpoint

The former `https://rpc.testnet.near.org` returned HTTP 429 with a deprecation
notice during the 9 November rehearsal. Both the finalized backend reader and the
wallet selector now pin `https://test.rpc.fastnear.com`, listed in the
[official NEAR RPC provider documentation](https://docs.near.org/api/rpc/providers).
Its reported chain ID was verified as testnet. No browser-provided RPC URL or
mainnet override is accepted. Reload an existing rehearsal tab after this change.
