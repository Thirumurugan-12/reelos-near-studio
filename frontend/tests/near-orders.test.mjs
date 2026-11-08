import test from "node:test";
import assert from "node:assert/strict";
import { nearAmount, orderCall, orderActions } from "../lib/near-orders.ts";
const now = 1900000000000;
const order = {
  id: "a".repeat(32),
  project_id: "c".repeat(32),
  contract_id: "escrow.testnet",
  config: {
    provider: "studio.testnet",
    price: "100000000000000000000000",
    storage_fee: "20000000000000000000000",
  },
  request: { client: "client.testnet" },
  brief_hash: "b".repeat(64),
  deadline_ns: String(BigInt(now + 86400000) * 1000000n),
  delivery_hash: "d".repeat(64),
};
const funded = {
  client: "client.testnet",
  amount: order.config.price,
  brief_hash: order.brief_hash,
  deadline_ns: order.deadline_ns,
  status: "funded",
  delivery_hash: null,
};
test("NEAR amounts remain exact to one yocto", () => {
  assert.equal(
    nearAmount("100000000000000000000001"),
    "0.100000000000000000000001",
  );
  assert.equal(nearAmount("0"), "0");
  assert.throws(() => nearAmount("1e24"));
});
test("funding attaches editing price plus storage", () => {
  const call = orderCall("fund", order, null, "client.testnet", now);
  assert.equal(call.deposit, "120000000000000000000000");
  assert.equal(call.method, "fund_job");
  assert.equal(call.args.brief_hash, order.brief_hash);
});
test("provider alone can publish the rendered artifact digest", () => {
  assert.deepEqual(orderActions(order, funded, "studio.testnet", now), [
    "deliver",
  ]);
  assert.throws(() =>
    orderCall("deliver", order, funded, "client.testnet", now),
  );
});
test("approval requires the delivered digest to match the rendered file", () => {
  const delivered = {
    ...funded,
    status: "delivered",
    delivery_hash: order.delivery_hash,
  };
  assert.equal(
    orderCall("approve", order, delivered, "client.testnet", now).method,
    "approve_job",
  );
  assert.throws(() =>
    orderCall(
      "approve",
      order,
      { ...delivered, delivery_hash: "e".repeat(64) },
      "client.testnet",
      now,
    ),
  );
});
test("refund opens exactly at deadline and only for client", () => {
  const after = Number(BigInt(order.deadline_ns) / 1000000n);
  assert.deepEqual(orderActions(order, funded, "client.testnet", after), [
    "refund",
  ]);
  assert.deepEqual(orderActions(order, funded, "stranger.testnet", after), []);
  assert.throws(() =>
    orderCall("refund", order, funded, "client.testnet", now),
  );
});
test("pending and terminal states never offer another transfer", () => {
  for (const status of ["paying", "paid", "refunding", "refunded"])
    assert.deepEqual(
      orderActions(
        order,
        { ...funded, status },
        "client.testnet",
        now + 86400000,
      ),
      [],
    );
});
test("mismatched chain payment cannot authorize an action", () => {
  assert.deepEqual(
    orderActions(order, { ...funded, amount: "1" }, "studio.testnet", now),
    [],
  );
});
test("funding rejects mainnet contracts, strangers and near-expired quotes", () => {
  assert.throws(() =>
    orderCall(
      "fund",
      { ...order, contract_id: "escrow.near" },
      null,
      "client.testnet",
      now,
    ),
  );
  assert.throws(() => orderCall("fund", order, null, "stranger.testnet", now));
  assert.deepEqual(
    orderActions(order, null, "client.testnet", now + 86400000 - 60000),
    [],
  );
});
