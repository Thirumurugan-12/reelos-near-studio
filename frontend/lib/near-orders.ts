export type StudioConfig = {
  provider: string;
  price: string;
  storage_fee: string;
};
export type NearConfig = {
  enabled: boolean;
  network: "testnet";
  contract_id: string | null;
  config?: StudioConfig;
};
export type ChainJob = {
  client: string;
  amount: string;
  brief_hash: string;
  deadline_ns: string;
  delivery_hash: string | null;
  status: "funded" | "delivered" | "paying" | "paid" | "refunding" | "refunded";
};
export type Order = {
  id: string;
  project_id: string;
  contract_id: string;
  config: StudioConfig;
  request: {
    client: string;
    asset_id: string;
    instruction: string;
    subject_prompt: string;
    output_mode: string;
  };
  brief_hash: string;
  deadline_ns: string;
  delivery_hash: string | null;
  preview_url: string | null;
  render: {
    id: string;
    status: string;
    stage: string;
    error?: string;
    progress: number | null;
  } | null;
};
export type OrderAction = "fund" | "deliver" | "approve" | "refund";
export type OrderCall = {
  receiverId: string;
  method: string;
  args: Record<string, string>;
  deposit: string;
};
const HEX = /^[a-f0-9]{64}$/;
const ACCOUNT = /^(([a-z0-9]+[-_])*[a-z0-9]+\.)*([a-z0-9]+[-_])*[a-z0-9]+$/;
function amount(value: string): bigint {
  if (!/^(0|[1-9][0-9]{0,38})$/.test(value) || BigInt(value) >= 2n ** 128n)
    throw new Error("Invalid NEAR amount.");
  return BigInt(value);
}
export function nearAmount(value: string): string {
  const n = amount(value),
    unit = 10n ** 24n;
  const fraction = (n % unit).toString().padStart(24, "0").replace(/0+$/, "");
  return `${n / unit}${fraction ? `.${fraction}` : ""}`;
}
function validOrder(order: Order): boolean {
  return (
    order.contract_id.length <= 64 &&
    ACCOUNT.test(order.contract_id) &&
    order.contract_id.endsWith(".testnet") &&
    /^[a-f0-9]{32}$/.test(order.id) &&
    HEX.test(order.brief_hash) &&
    /^[1-9][0-9]{0,19}$/.test(order.deadline_ns) &&
    BigInt(order.deadline_ns) < 2n ** 64n &&
    amount(order.config.price) > 0n &&
    amount(order.config.storage_fee) > 0n &&
    amount(order.config.price) + amount(order.config.storage_fee) < 2n ** 128n
  );
}
export function matchingJob(order: Order, job: ChainJob): boolean {
  return (
    job.client === order.request.client &&
    job.amount === order.config.price &&
    job.brief_hash === order.brief_hash &&
    job.deadline_ns === order.deadline_ns
  );
}
export function orderActions(
  order: Order,
  job: ChainJob | null,
  account: string,
  now = Date.now(),
): OrderAction[] {
  try {
    if (!validOrder(order)) return [];
    const until =
      BigInt(order.deadline_ns) - BigInt(Math.floor(now)) * 1000000n;
    if (!job)
      return account === order.request.client &&
        until >= 3600000000000n &&
        until <= 604800000000000n
        ? ["fund"]
        : [];
    if (!matchingJob(order, job)) return [];
    if (["funded", "delivered"].includes(job.status) && until <= 0n)
      return account === job.client ? ["refund"] : [];
    if (until <= 0n) return [];
    if (
      job.status === "funded" &&
      account === order.config.provider &&
      order.delivery_hash &&
      HEX.test(order.delivery_hash)
    )
      return ["deliver"];
    if (
      job.status === "delivered" &&
      account === job.client &&
      order.delivery_hash &&
      job.delivery_hash === order.delivery_hash
    )
      return ["approve"];
    return [];
  } catch {
    return [];
  }
}
export function orderCall(
  action: OrderAction,
  order: Order,
  job: ChainJob | null,
  account: string,
  now = Date.now(),
): OrderCall {
  if (!orderActions(order, job, account, now).includes(action))
    throw new Error(
      "This action is unavailable. Refresh the job and check your wallet account.",
    );
  const args: Record<string, string> = { job_id: order.id };
  if (action === "fund")
    Object.assign(args, {
      brief_hash: order.brief_hash,
      deadline_ns: order.deadline_ns,
    });
  if (action === "deliver") args.delivery_hash = order.delivery_hash!;
  return {
    receiverId: order.contract_id,
    method: {
      fund: "fund_job",
      deliver: "deliver_job",
      approve: "approve_job",
      refund: "refund_job",
    }[action],
    args,
    deposit:
      action === "fund"
        ? (
            amount(order.config.price) + amount(order.config.storage_fee)
          ).toString()
        : "0",
  };
}
