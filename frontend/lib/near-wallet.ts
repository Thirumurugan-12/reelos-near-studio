import type {
  InjectedWallet,
  WalletSelector,
} from "@near-wallet-selector/core";
import type { OrderCall } from "./near-orders";
let pending: Promise<WalletSelector> | undefined;
let walletNetwork = "testnet";
export function walletSelector() {
  if (!pending)
    pending = Promise.all([
      import("@near-wallet-selector/core"),
      import("@near-wallet-selector/meteor-wallet"),
    ])
      .then(([core, meteor]) =>
        core.setupWalletSelector({
          network: "testnet",
          modules: [meteor.setupMeteorWallet()],
          debug: false,
        }),
      )
      .then((selector) => {
        selector.on("networkChanged", (event) => {
          walletNetwork = event.networkId;
        });
        return selector;
      })
      .catch((error) => {
        pending = undefined;
        throw error;
      });
  return pending;
}
export function requireTestnet(selector: WalletSelector) {
  if (
    walletNetwork !== "testnet" ||
    selector.options.network.networkId !== "testnet"
  )
    throw new Error("Only NEAR testnet is supported.");
}
export async function connectWallet(contractId?: string) {
  const selector = await walletSelector();
  const wallet = await selector.wallet<InjectedWallet>("meteor-wallet");
  const accounts = await wallet.signIn(
    contractId
      ? {
          contractId,
          methodNames: ["fund_job", "deliver_job", "approve_job", "refund_job"],
        }
      : {},
  );
  if (!accounts.length) throw new Error("No wallet account selected.");
  return accounts[0].accountId;
}
export async function disconnectWallet() {
  const wallet = await (
    await walletSelector()
  ).wallet<InjectedWallet>("meteor-wallet");
  await wallet.signOut();
}
export async function signOrder(call: OrderCall, account: string) {
  const selector = await walletSelector();
  if (
    walletNetwork !== "testnet" ||
    selector.options.network.networkId !== "testnet" ||
    !call.receiverId.endsWith(".testnet")
  )
    throw new Error("Only NEAR testnet is supported.");
  const wallet = await selector.wallet<InjectedWallet>("meteor-wallet");
  const accounts = await wallet.getAccounts();
  if (!accounts.some((a) => a.accountId === account))
    throw new Error("Wallet account changed. Reconnect before signing.");
  const { actionCreators } = await import("@near-wallet-selector/core");
  return wallet.signAndSendTransaction({
    signerId: account,
    receiverId: call.receiverId,
    actions: [
      actionCreators.functionCall(
        call.method,
        call.args,
        100000000000000n,
        BigInt(call.deposit),
      ),
    ],
  });
}
