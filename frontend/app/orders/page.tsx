"use client";
import Link from "next/link";
import { useOrders } from "../../lib/use-orders";
import { OrderForm } from "../../components/order-form";
import { PaymentSummary } from "../../components/payment-summary";
import { OrderReview } from "../../components/order-review";
import styles from "./orders.module.css";

export default function PaidStudio() {
  const s = useOrders();
  const ready = !!s.config?.enabled;
  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <Link href="/" className="wordmark" aria-label="ReelOS editor">
          reel<span>os</span>
        </Link>
        <span className={styles.network}>NEAR TESTNET · No real funds</span>
        <Link href="/">Back to editor ↗</Link>
      </header>
      <div className={styles.intro}>
        <p className={styles.eyebrow}>REELOS STUDIO / PAID EDITING</p>
        <h1>Create an editing order.</h1>
        <p>
          Fund a creative brief. Review the finished video. Release the editing
          payment when you approve.
        </p>
      </div>
      {s.error && (
        <div className={styles.alert} role="alert">
          <p>{s.error}</p>
          <button onClick={s.check} disabled={!!s.busy}>
            Refresh status
          </button>
        </div>
      )}
      {!s.config && !s.error && <p role="status">Connecting to the studio…</p>}
      {s.config && !ready && (
        <section className={styles.notice} aria-labelledby="opening">
          <span className={styles.dot} />
          <div>
            <h2 id="opening">Testnet payments are not open yet</h2>
            <p>
              The escrow contract is awaiting deployment. You can prepare
              footage in the editor; funding and wallet signing will open once
              the contract is live.
            </p>
            <Link href="/">Prepare your footage →</Link>
          </div>
        </section>
      )}
      <div className={styles.grid}>
        <section className={styles.workspace}>
          <div className={styles.sectionTitle}>
            <span>01</span>
            <h2>
              {s.order ? "Your editing order" : "Give your editor a brief"}
            </h2>
          </div>
          {s.order ? (
            <OrderReview
              order={s.order}
              chain={s.chain}
              account={s.account}
              block={s.block}
              verified={s.verified}
              now={s.now}
            />
          ) : (
            <OrderForm s={s} />
          )}
          {!!s.history.length && (
            <nav className={styles.saved} aria-label="Saved editing orders">
              <h3>Saved orders</h3>
              <ul>
                {s.history.map((item) => (
                  <li key={item.id}>
                    <a
                      href={`/orders?project=${s.project?.id || s.order?.project_id}&order=${item.id}`}
                    >
                      {item.instruction}
                    </a>
                    <time>
                      {new Date(item.created_at * 1000).toLocaleString()}
                    </time>
                  </li>
                ))}
              </ul>
            </nav>
          )}
        </section>
        <PaymentSummary s={s} />
      </div>
      <footer className={styles.footer}>
        A local ReelOS workspace · Payments on NEAR testnet · Provider confirms
        delivery in their wallet
      </footer>
    </main>
  );
}
