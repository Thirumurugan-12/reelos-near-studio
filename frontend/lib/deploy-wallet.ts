import type { InjectedWallet } from "@near-wallet-selector/core";
import { requireTestnet, walletSelector } from "./near-wallet";
import { reviewDeployment } from "./near-deployment";
import type { DeploymentManifest } from "./near-deployment";

export async function deployFromWallet(
  manifest: DeploymentManifest,
  studio: string,
) {
  const response = await fetch("/api/near/deployment/wasm", {
    cache: "no-store",
  });
  if (!response.ok)
    throw new Error(
      "The compiled contract is unavailable. Refresh and try again.",
    );
  const wasm = new Uint8Array(await response.arrayBuffer());
  const plan = await reviewDeployment(manifest, studio, wasm);
  const selector = await walletSelector();
  requireTestnet(selector);
  const wallet = await selector.wallet<InjectedWallet>("meteor-wallet");
  if (!(await wallet.getAccounts()).some((a) => a.accountId === studio))
    throw new Error("Wallet account changed. Reconnect before deploying.");
  const { actionCreators } = await import("@near-wallet-selector/core");
  return wallet.signAndSendTransaction({
    signerId: studio,
    receiverId: plan.receiverId,
    actions: [
      actionCreators.createAccount(),
      actionCreators.transfer(BigInt(plan.deposit)),
      actionCreators.deployContract(wasm),
      actionCreators.functionCall(
        plan.initializer,
        { price: plan.price },
        100000000000000n,
        0n,
      ),
    ],
  });
}
