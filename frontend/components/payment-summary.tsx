import type { useOrders } from "../lib/use-orders";
import { nearAmount, orderActions, matchingJob } from "../lib/near-orders";
import styles from "../app/orders/orders.module.css";
export function PaymentSummary({ s }: { s: ReturnType<typeof useOrders> }) {
  const ready = !!s.config?.enabled;
  const cfg = s.order?.config || s.config?.config;
  const actions =
    s.order && s.verified && s.config?.contract_id === s.order.contract_id
      ? orderActions(s.order, s.chain, s.account, s.now)
      : [];
  const canStart =
    s.order &&
    s.verified &&
    s.chain?.status === "funded" &&
    matchingJob(s.order, s.chain) &&
    !s.order.render &&
    BigInt(s.order.deadline_ns) > BigInt(s.now) * 1000000n;
  return (
    <aside className={styles.summary} aria-label="Payment summary">
      <div className={styles.sectionTitle}>
        <span>02</span>
        <h2>Payment, with your approval</h2>
      </div>
      <dl className={styles.costs}>
        <div>
          <dt>Editing payment</dt>
          <dd>
            {cfg ? nearAmount(cfg.price) : "—"} <small>NEAR</small>
          </dd>
        </div>
        <div>
          <dt>
            Storage fee <small>retained</small>
          </dt>
          <dd>
            {cfg ? nearAmount(cfg.storage_fee) : "—"} <small>NEAR</small>
          </dd>
        </div>
        <div className={styles.total}>
          <dt>Total deposit</dt>
          <dd>
            {cfg
              ? nearAmount(
                  (BigInt(cfg.price) + BigInt(cfg.storage_fee)).toString(),
                )
              : "—"}{" "}
            <small>NEAR</small>
          </dd>
        </div>
      </dl>
      <p className={styles.hint}>
        Test tokens only. Network gas is additional and shown by your wallet.
        Prices appear after the contract is connected.
      </p>
      <ol className={styles.steps}>
        <li>
          <strong>Fund the brief</strong>
          <span>Your editing payment waits in escrow.</span>
        </li>
        <li>
          <strong>Watch your edit</strong>
          <span>The studio renders and publishes a delivery digest.</span>
        </li>
        <li>
          <strong>Approve the result</strong>
          <span>Only the client can release payment to the studio.</span>
        </li>
      </ol>
      <p className={styles.terms}>
        After the 24-hour deadline, the client can reclaim an unreleased editing
        payment. The storage fee is retained. Approval must happen before the
        deadline.
      </p>
      <div className={styles.wallet}>
        <span>
          {s.account ? "Connected account" : "Connect when you’re ready"}
        </span>
        {s.account && <strong>{s.account}</strong>}
        <button
          onClick={s.account ? s.disconnect : s.connect}
          disabled={!ready || !!s.busy}
        >
          {s.account ? "Disconnect wallet" : "Connect Meteor Wallet"}
        </button>
      </div>
      {s.order && (
        <div className={styles.actionStack}>
          {actions.map((action) => (
            <button
              className={styles.primary}
              key={action}
              disabled={!!s.busy}
              onClick={() => s.transact(action)}
            >
              {
                {
                  fund: "Fund editing order",
                  deliver: "Publish delivery in wallet",
                  approve: "Approve edit & release payment",
                  refund: "Refund editing payment",
                }[action]
              }
            </button>
          ))}
          {canStart && (
            <button
              className={styles.primary}
              disabled={!!s.busy}
              onClick={s.start}
            >
              Start AI editing
            </button>
          )}
          <button onClick={s.check} disabled={!!s.busy}>
            Refresh contract status
          </button>
          <button onClick={s.reset} disabled={!!s.busy}>
            Prepare another order
          </button>
          <p className={styles.hint}>
            Keep this order’s URL to return to it. Signing does not mean
            settlement is confirmed; the status comes from finalized chain
            state.
          </p>
        </div>
      )}
      <p className={styles.status} role="status" aria-live="polite">
        {s.busy || s.notice || ""}
      </p>
    </aside>
  );
}
