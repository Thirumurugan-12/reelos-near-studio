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
