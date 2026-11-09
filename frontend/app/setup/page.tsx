"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, post } from "../../lib/api";
import type { DeploymentManifest } from "../../lib/near-deployment";
import type { NearConfig } from "../../lib/near-orders";
import styles from "../orders/orders.module.css";
import local from "./setup.module.css";

export default function Setup() {
  const [manifest, setManifest] = useState<DeploymentManifest>();
  const [studio, setStudio] = useState("");
  const [contract, setContract] = useState("");
  const [consent, setConsent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [verified, setVerified] = useState(false);
  const lock = useRef(false);
  useEffect(() => {
    api<DeploymentManifest>("/near/deployment")
      .then(setManifest)
      .catch((e) => setError(e.message));
    api<NearConfig>("/near/config")
      .then((config) => {
        if (config.enabled && config.config && config.contract_id) {
          setStudio(config.config.provider);
          setContract(config.contract_id);
        }
      })
      .catch((e) => setError(e.message));
  }, []);
  async function verify() {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError("");
    setVerified(false);
    try {
      await post("/near/deployment/activate", {
        studio,
        contract_id: contract,
        allow_upgradeable: consent,
      });
      setVerified(true);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Verification failed. Check the account IDs and try again.",
      );
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  const valid =
    studio.endsWith(".testnet") &&
    contract.endsWith(".testnet") &&
    studio !== contract;
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
        <h1>Connect your deployed escrow.</h1>
        <p>
          Deploy from the NEAR CLI with a dedicated developer account, then
          verify it here. Meteor handles customer payments and studio delivery
          signatures.
        </p>
      </div>
      <section className={styles.notice}>
        <div>
          <h2>Meteor blocks contract deployment from apps.</h2>
          <p>
            Cancel the blocked wallet request. Setup uses the official CLI; this
            page only reads chain state and saves local configuration.
          </p>
          <a
            href="https://docs.near.org/tools/cli#deploy"
            target="_blank"
            rel="noreferrer"
          >
            NEAR CLI deployment guide ↗
          </a>
        </div>
      </section>
      {error && (
        <div className={styles.alert} role="alert">
          {error}
        </div>
      )}
      {verified && (
        <section className={styles.notice} role="status">
          <div>
            <h2>Contract verified. Your studio is ready.</h2>
            <p>The finalized code, provider and pricing match this build.</p>
            <Link href="/orders">Open paid editing →</Link>
          </div>
        </section>
      )}
      <div className={styles.grid}>
        <section className={styles.workspace}>
          <div className={styles.sectionTitle}>
            <span>01</span>
            <h2>Verify deployment accounts</h2>
          </div>
          <label className={local.field}>
            Studio / provider account
            <input
              value={studio}
              placeholder="your-studio.testnet"
              disabled={busy}
              onChange={(e) => {
                setStudio(e.target.value.trim());
                setVerified(false);
              }}
            />
          </label>
          <label className={local.field}>
            Deployed contract account
            <input
              value={contract}
              placeholder="your-escrow.testnet"
              disabled={busy}
              onChange={(e) => {
                setContract(e.target.value.trim());
                setVerified(false);
              }}
            />
          </label>
          <p>
            Keep deployment keys in your local CLI credential store. This app
            accepts public account IDs only.
          </p>
          <details className={styles.receipt}>
            <summary>Review the compiled contract</summary>
            <p>
              Size: {manifest?.wasm_bytes.toLocaleString() || "Loading…"} bytes
            </p>
            <p>
              SHA-256: <code>{manifest?.wasm_sha256 || "Loading…"}</code>
            </p>
            <p>
              CLI initialization uses <code>new</code> with your studio provider
              and the fixed 0.1 NEAR price, in the same transaction as
              deployment.
            </p>
          </details>
        </section>
        <aside className={styles.summary}>
          <div className={styles.sectionTitle}>
            <span>02</span>
            <h2>Review the testnet terms</h2>
          </div>
          <dl className={styles.details}>
            <div>
              <dt>Editing price</dt>
              <dd>0.1 testnet NEAR</dd>
            </div>
            <div>
              <dt>Order storage</dt>
              <dd>0.02 testnet NEAR, retained</dd>
            </div>
            <div>
              <dt>Customer total</dt>
              <dd>0.12 testnet NEAR + gas</dd>
            </div>
            <div>
              <dt>Recommended deployment reserve</dt>
              <dd>At least 3 testnet NEAR</dd>
            </div>
          </dl>
          <label className={local.consent}>
            <input
              type="checkbox"
              checked={consent}
              disabled={busy}
              onChange={(e) => setConsent(e.target.checked)}
            />
            <span>
              I understand that a contract with a developer full-access key can
              be upgraded or deleted. This deployment is for testnet rehearsal.
            </span>
          </label>
          <button
            className={styles.primary}
            disabled={!valid || busy || !manifest || !consent}
            onClick={verify}
          >
            {busy
              ? "Verifying finalized deployment…"
              : "Verify & activate local studio"}
          </button>
          <p className={styles.hint}>
            Verification checks the deployed Wasm, provider, price and access
            keys. It sends no transaction.
          </p>
        </aside>
      </div>
    </main>
  );
}
