import type { ChainJob, Order } from "../lib/near-orders";
import { matchingJob } from "../lib/near-orders";
import styles from "../app/orders/orders.module.css";
export function OrderReview({
  order,
  chain,
  account,
  block,
  verified,
  now,
}: {
  order: Order;
  chain: ChainJob | null;
  account: string;
  block: number | null;
  verified: boolean;
  now: number;
}) {
  const states = {
    funded: "Payment held in escrow",
    delivered: "Delivery published · awaiting client approval",
    paying: "Payment transfer pending",
    paid: "Payment released to studio",
    refunding: "Refund transfer pending",
    refunded: "Editing payment refunded",
  };
  const matches = !chain || matchingJob(order, chain);
  const deadline = new Date(Number(BigInt(order.deadline_ns) / 1000000n));
  return (
    <div className={styles.review}>
      <div className={styles.jobStatus} role="status" aria-live="polite">
        <span className={styles.dot} />
        {!verified
          ? "Checking finalized state…"
          : !matches
            ? "Payment does not match this order"
            : chain
              ? states[chain.status]
              : "Awaiting funding"}
      </div>
      <h3>Your creative direction</h3>
      <p className={styles.brief}>{order.request.instruction}</p>
      <dl className={styles.details}>
        <div>
          <dt>Client</dt>
          <dd>
            {order.request.client}
            {account === order.request.client ? " · you" : ""}
          </dd>
        </div>
        <div>
          <dt>Studio</dt>
          <dd>
            {order.config.provider}
            {account === order.config.provider ? " · you" : ""}
          </dd>
        </div>
        <div>
          <dt>Approval deadline</dt>
          <dd>
            {deadline.toLocaleString()}{" "}
            {now >= deadline.getTime() ? "· passed" : ""}
          </dd>
        </div>
        <div>
          <dt>Order</dt>
          <dd>
            <code>{order.id}</code>
          </dd>
        </div>
      </dl>
      {block && (
        <p className={styles.hint}>
          Verified at finalized block {block.toLocaleString()}.
        </p>
      )}
      {order.render && (
        <section className={styles.render}>
          <h3>Your edit</h3>
          <p role="status">{order.render.stage}</p>
          {order.render.progress !== null && (
            <progress
              aria-label="Editing progress"
              max={1}
              value={order.render.progress}
            />
          )}
          {order.render.status === "failed" && (
            <p role="alert">
              {order.render.error || "The edit needs attention."} Paid work is
              not retried automatically. Your unreleased payment can be refunded
              after the deadline.
            </p>
          )}
          {order.render.status === "needs_subject" && (
            <p role="alert">
              The video contains multiple subjects. This order needs studio
              review; it will not be delivered automatically. The client can
              refund after the deadline.
            </p>
          )}
        </section>
      )}
      {order.preview_url && (
        <div className={styles.output}>
          <video
            controls
            preload="metadata"
            src={order.preview_url}
            aria-label="Completed editing preview"
          />
          {matches && chain?.status === "paid" && (
            <a className={styles.primary} href={order.preview_url} download>
              Download your video
            </a>
          )}
          {chain?.status === "funded" && (
            <p>
              The render is ready. The studio must publish its delivery digest
              before the client can approve payment.
            </p>
          )}
          {chain?.status === "delivered" && (
            <p>
              Review the video before approving. Approval releases the editing
              payment to the studio.
            </p>
          )}
        </div>
      )}
      {chain?.status === "delivered" &&
        order.delivery_hash &&
        chain.delivery_hash !== order.delivery_hash && (
          <p role="alert">
            The published delivery digest does not match this video. Approval is
            unavailable; ask the studio to review it or refund after the
            deadline.
          </p>
        )}
      <details className={styles.receipt}>
        <summary>Contract receipt details</summary>
        <p>
          Contract: <code>{order.contract_id}</code>
        </p>
        <p>
          Brief digest: <code>{order.brief_hash}</code>
        </p>
        {order.delivery_hash && (
          <p>
            Rendered artifact digest: <code>{order.delivery_hash}</code>
          </p>
        )}
        <a
          href={`https://testnet.nearblocks.io/address/${order.contract_id}`}
          target="_blank"
          rel="noreferrer"
        >
          Inspect testnet contract ↗
        </a>
      </details>
    </div>
  );
}
