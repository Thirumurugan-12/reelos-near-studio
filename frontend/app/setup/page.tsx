"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, post } from "../../lib/api";
import type { DeploymentManifest } from "../../lib/near-deployment";
import { connectWallet, disconnectWallet } from "../../lib/near-wallet";
import { deployFromWallet } from "../../lib/deploy-wallet";
import styles from "../orders/orders.module.css";
import local from "./setup.module.css";

export default function Setup() {
  const [manifest, setManifest] = useState<DeploymentManifest>();
  const [account, setAccount] = useState("");
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [verified, setVerified] = useState(false);
  const lock = useRef(false);
  useEffect(() => {
    api<DeploymentManifest>("/near/deployment")
      .then(setManifest)
      .catch((e) => setError(e.message));
  }, []);
  async function run(label: string, fn: () => Promise<void>) {
    if (lock.current) return;
    lock.current = true;
    setBusy(label);
    setError("");
    try {
      await fn();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Setup did not complete. Try verifying before submitting another transaction.",
      );
    } finally {
      lock.current = false;
      setBusy("");
    }
  }
  async function verify() {
    await post("/near/deployment/activate", { studio: account });
    setVerified(true);
  }
  function deploy() {
    void run("Review the transaction in Meteor…", async () => {
      if (!manifest || !consent || !account)
        throw new Error(
          "Connect your wallet and review the deployment terms first.",
        );
      try {
        await deployFromWallet(manifest, account);
      } catch {
        throw new Error(
          "Wallet deployment did not complete. If you signed, verify the deployment before trying again.",
        );
      }
      setBusy("Checking finalized contract code and settings…");
      await verify();
    });
  }
  const valid =
    account.endsWith(".testnet") && `escrow.${account}`.length <= 64;
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <Link href="/" className="wordmark">
          reel<span>os</span>
        </Link>
        <span className={styles.network}>STUDIO SETUP · NEAR TESTNET</span>
        <Link href="/orders">Paid studio ↗</Link>
      </header>
      <div className={styles.intro}>
        <p className={styles.eyebrow}>ONE-TIME STUDIO SETUP</p>
        <h1>Put your escrow on testnet.</h1>
        <p>
          Your wallet creates a separate contract account. Your studio wallet
          keeps its remaining balance and stays in your control.
        </p>
      </div>
      {error && (
        <div className={styles.alert} role="alert">
          {error}
        </div>
      )}
      {verified && (
        <section className={styles.notice} role="status">
          <div>
            <h2>Contract verified. Your studio is ready.</h2>
            <p>
              The deployed Wasm, provider, pricing and absence of access keys
              match this setup.
            </p>
            <Link href="/orders">Open paid editing →</Link>
          </div>
        </section>
      )}
      <div className={styles.grid}>
        <section className={styles.workspace}>
          <div className={styles.sectionTitle}>
            <span>01</span>
            <h2>Connect your studio wallet</h2>
          </div>
          <p>
            Choose your studio’s named <strong>.testnet</strong> account in
            Meteor. Keep your recovery phrase and private key in your wallet.
          </p>
          <button
            disabled={!!busy || !manifest}
            onClick={() =>
              run("Opening Meteor…", async () => {
                if (account) {
                  await disconnectWallet();
                  setAccount("");
                  setConsent(false);
                  setVerified(false);
                } else {
                  setAccount(await connectWallet());
                  setConsent(false);
                }
              })
            }
          >
            {account ? "Disconnect wallet" : "Connect Meteor Wallet"}
          </button>
          <dl className={styles.details}>
            <div>
              <dt>Studio / provider</dt>
              <dd>{account || "Connect a named testnet wallet"}</dd>
            </div>
            <div>
              <dt>Escrow account</dt>
              <dd>
                {account
                  ? `escrow.${account}`
                  : "Derived from your connected studio account"}
              </dd>
            </div>
            <div>
              <dt>Deployment balance</dt>
              <dd>3 testnet NEAR, plus network gas</dd>
            </div>
            <div>
              <dt>Editing price</dt>
              <dd>0.1 testnet NEAR per order</dd>
            </div>
            <div>
              <dt>Order storage</dt>
              <dd>0.02 testnet NEAR, retained per order</dd>
            </div>
          </dl>
          {account && !valid && (
            <p role="alert">
              Use a named .testnet account short enough to create an escrow
              subaccount.
            </p>
          )}
          <details className={styles.receipt}>
            <summary>Review the compiled contract</summary>
            <p>
              Size: {manifest?.wasm_bytes.toLocaleString() || "Loading…"} bytes
            </p>
            <p>
              SHA-256: <code>{manifest?.wasm_sha256 || "Loading…"}</code>
            </p>
            <p>
              Deployment consists of account creation, a 3 NEAR transfer,
              contract code deployment, and initialization in one atomic batch.
              No access keys are added.
            </p>
          </details>
        </section>
        <aside className={styles.summary}>
          <div className={styles.sectionTitle}>
            <span>02</span>
            <h2>Review before signing</h2>
          </div>
          <ol className={styles.steps}>
            <li>
              <strong>3 testnet NEAR moves into escrow</strong>
              <span>
                This covers code and state storage. It is separate from customer
                payments.
              </span>
            </li>
            <li>
              <strong>The contract account has no keys</strong>
              <span>
                Its code cannot be upgraded or removed. The deployment balance
                stays in that account; this contract has no withdrawal method
                for it.
              </span>
            </li>
            <li>
              <strong>You sign in Meteor</strong>
              <span>
                The app never receives your studio wallet’s private key. Only
                finalized verification enables paid orders.
              </span>
            </li>
          </ol>
          <label className={local.consent}>
            <input
              type="checkbox"
              checked={consent}
              disabled={!valid || !!busy}
              onChange={(e) => setConsent(e.target.checked)}
            />
            <span>
              I understand this creates a permanent testnet escrow and transfers
              3 testnet NEAR into it.
            </span>
          </label>
          <div className={styles.actionStack}>
            <button
              className={styles.primary}
              disabled={!valid || !consent || !!busy || !manifest || verified}
              onClick={deploy}
            >
              Review & deploy in Meteor
            </button>
            <button
              disabled={!valid || !!busy}
              onClick={() => run("Verifying finalized deployment…", verify)}
            >
              Verify an existing deployment
            </button>
          </div>
          <p className={styles.status} role="status" aria-live="polite">
            {busy}
          </p>
          <p className={styles.hint}>
            If the wallet closes or the network times out after signing, use
            Verify before retrying. An existing account cannot be created twice.
          </p>
        </aside>
      </div>
    </main>
  );
}
