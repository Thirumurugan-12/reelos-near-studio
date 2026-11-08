"use client";
import { useState } from "react";
import Link from "next/link";
import type { useOrders } from "../lib/use-orders";
import styles from "../app/orders/orders.module.css";
export function OrderForm({ s }: { s: ReturnType<typeof useOrders> }) {
  const [asset, setAsset] = useState("");
  const [instruction, setInstruction] = useState("");
  const [subject, setSubject] = useState("person");
  const sources = s.project?.assets.filter((a) => a.role === "source") || [];
  const selectedAsset = sources.some((a) => a.id === asset)
    ? asset
    : sources[0]?.id || "";
  const ready = !!s.config?.enabled;
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void s.create(selectedAsset, instruction, subject);
      }}
    >
      <label htmlFor="paid-project">Project</label>
      <select
        id="paid-project"
        value={s.project?.id || ""}
        disabled={!!s.busy}
        onChange={(e) => {
          setAsset("");
          void s.select(e.target.value);
        }}
      >
        <option value="" disabled>
          Choose an editor project
        </option>
        {s.projects.map((p) => (
          <option key={p.id} value={p.id}>
            {p.name}
          </option>
        ))}
      </select>
      {!s.projects.length && (
        <p className={styles.hint}>
          No projects yet. <Link href="/">Add footage in the editor</Link> to
          begin.
        </p>
      )}
      <label htmlFor="paid-source">Source footage</label>
      <select
        id="paid-source"
        value={selectedAsset}
        disabled={!sources.length || !!s.busy}
        onChange={(e) => setAsset(e.target.value)}
      >
        <option value="" disabled>
          Choose a source video
        </option>
        {sources.map((a) => (
          <option key={a.id} value={a.id}>
            {a.name}
          </option>
        ))}
      </select>
      <p className={styles.hint}>
        A 15–30 second reel from one source video. For this first demo, use a
        clip with one clearly visible person.
      </p>
      <label htmlFor="paid-direction">What should the edit feel like?</label>
      <textarea
        id="paid-direction"
        maxLength={2000}
        rows={4}
        required
        value={instruction}
        onChange={(e) => setInstruction(e.target.value)}
        placeholder="A confident opening, a bold title, and a subtle spotlight on the speaker."
      />
      <label htmlFor="paid-subject">Who should we follow?</label>
      <input
        id="paid-subject"
        maxLength={120}
        required
        value={subject}
        onChange={(e) => setSubject(e.target.value)}
      />
      <p className={styles.hint}>
        Directions and footage stay in this local workspace. Only their digest
        and payment terms go onchain.
      </p>
      <button
        className={styles.primary}
        type="submit"
        disabled={
          !ready ||
          !selectedAsset ||
          !s.account ||
          !instruction.trim() ||
          !subject.trim() ||
          !!s.busy
        }
      >
        Review editing order →
      </button>
      <p className={styles.hint}>
        Reviewing an order does not send a transaction.
      </p>
    </form>
  );
}
