"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api } from "../../lib/api";
import { connectWallet, signOrder } from "../../lib/near-wallet";
import { nearAmount } from "../../lib/near-orders";
import type { ChainJob } from "../../lib/near-orders";
import styles from "../orders/orders.module.css";

type Evidence = {
  contract_id: string;
  provider: string;
  client: string;
  job_id: string;
  brief_hash: string;
  deadline_ns: string;
  delivery_hash: string;
  price: string;
  storage_fee: string;
  total_deposit: string;
  chain: ChainJob | null;
  block_height: number;
  video_url: string;
  fund_tx: string | null;
  delivery_tx: string | null;
  approve_tx: string | null;
};
export default function Rehearsal() {
  const [data, setData] = useState<Evidence>();
  const [account, setAccount] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const lock = useRef(false);
  async function refresh() {
    const fresh = await api<Evidence>("/near/rehearsal");
    setData(fresh);
    return fresh;
  }
  useEffect(() => {
    const check = () => refresh().catch((e) => setError(e.message));
    void check();
    const timer = setInterval(check, 5000);
    return () => clearInterval(timer);
  }, []);
  async function run(label: string, action: () => Promise<void>) {
    if (lock.current) return;
    lock.current = true;
    setBusy(label);
    setError("");
    try {
      await action();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "The request did not complete. Refresh chain state before retrying.",
      );
    } finally {
      lock.current = false;
      setBusy("");
    }
  }
  async function publish() {
    await run("Review the delivery signature in Meteor…", async () => {
      const fresh = await refresh();
      if (
        account !== fresh.provider ||
        fresh.chain?.status !== "funded" ||
        BigInt(fresh.deadline_ns) <= BigInt(Date.now()) * 1000000n
      )
        throw new Error(
          "Connect the studio provider and confirm the job is funded before publishing.",
        );
      await signOrder(
        {
          receiverId: fresh.contract_id,
          method: "deliver_job",
          args: { job_id: fresh.job_id, delivery_hash: fresh.delivery_hash },
          deposit: "0",
        },
        account,
      );
      await refresh();
    });
  }
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <Link href="/" className="wordmark">
          reel<span>os</span>
        </Link>
        <span className={styles.network}>
          CONTRACT REHEARSAL · NEAR TESTNET
        </span>
        <Link href="/orders">Paid studio ↗</Link>
      </header>
      <div className={styles.intro}>
        <p className={styles.eyebrow}>REAL TESTNET TRANSACTION PROOF</p>
        <h1>Verify the edit. Settle the job.</h1>
        <p>
          This rehearsal settles the existing rendered sample between a separate
          demo customer and your studio. It does not represent a new AI
          inference or a funded worker render.
        </p>
      </div>
      {error && (
        <div className={styles.alert} role="alert">
          {error}
        </div>
      )}
      {!data ? (
        <p role="status">Loading finalized rehearsal evidence…</p>
      ) : (
        <div className={styles.grid}>
          <section className={styles.workspace}>
            <div className={styles.sectionTitle}>
              <span>01</span>
              <h2>The delivered artifact</h2>
            </div>
            <video
              controls
              preload="metadata"
              src={data.video_url}
              style={{
                width: "100%",
                maxHeight: 480,
                background: "#101412",
                borderRadius: 8,
              }}
            />
            <dl className={styles.details}>
              <div>
                <dt>Customer</dt>
                <dd>{data.client}</dd>
              </div>
              <div>
                <dt>Studio provider</dt>
                <dd>{data.provider}</dd>
              </div>
              <div>
                <dt>Contract</dt>
                <dd>{data.contract_id}</dd>
              </div>
              <div>
                <dt>Job ID</dt>
                <dd>
                  <code>{data.job_id}</code>
                </dd>
              </div>
              <div>
                <dt>Export SHA-256</dt>
                <dd>
                  <code>{data.delivery_hash}</code>
                </dd>
              </div>
            </dl>
            <p className={styles.hint}>
              The server hashes the actual MP4 and checks the finalized client,
              amount, brief and deadline before returning signing details.
            </p>
          </section>
          <aside className={styles.summary}>
            <div className={styles.sectionTitle}>
              <span>02</span>
              <h2>Finalized payment state</h2>
            </div>
            <p className={styles.eyebrow}>
              {data.chain?.status || "Not funded yet"}
            </p>
            <dl className={styles.details}>
              <div>
                <dt>Editing payment</dt>
                <dd>{nearAmount(data.price)} NEAR</dd>
              </div>
              <div>
                <dt>Retained storage fee</dt>
                <dd>{nearAmount(data.storage_fee)} NEAR</dd>
              </div>
              <div>
                <dt>Customer deposit</dt>
                <dd>{nearAmount(data.total_deposit)} NEAR + gas</dd>
              </div>
              <div>
                <dt>Finalized block</dt>
                <dd>{data.block_height}</dd>
              </div>
              <div>
                <dt>Connected studio wallet</dt>
                <dd>{account || "Not connected"}</dd>
              </div>
            </dl>
            <div className={styles.actionStack}>
              <button
                disabled={!!busy}
                onClick={() =>
                  run("Opening Meteor…", async () =>
                    setAccount(await connectWallet(data.contract_id)),
                  )
                }
              >
                Connect studio wallet
              </button>
              <button
                className={styles.primary}
                disabled={
                  !!busy ||
                  account !== data.provider ||
                  data.chain?.status !== "funded"
                }
                onClick={publish}
              >
                Publish this export’s delivery hash
              </button>
              <button
                disabled={!!busy}
                onClick={() =>
                  run("Reading finalized chain state…", async () => {
                    await refresh();
                  })
                }
              >
                Refresh transaction proof
              </button>
            </div>
            <p className={styles.status} role="status">
              {busy}
            </p>
            <p className={styles.hint}>
              Publishing delivery attaches 0 NEAR, plus testnet gas. The
              separate customer must then approve the 0.1 NEAR release. The 0.02
              NEAR storage fee remains in escrow.
            </p>
            <ul>
              {(
                [
                  ["Funding", data.fund_tx],
                  ["Delivery", data.delivery_tx],
                  ["Client approval", data.approve_tx],
                ] as const
              ).map(([label, tx]) => (
                <li key={label}>
                  {tx ? (
                    <a
                      href={`https://explorer.testnet.near.org/transactions/${encodeURIComponent(tx)}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {label} receipt ↗
                    </a>
                  ) : (
                    `${label} receipt pending`
                  )}
                </li>
              ))}
            </ul>
          </aside>
        </div>
      )}
    </main>
  );
}
