import assert from "node:assert/strict";
import test from "node:test";
import { Worker } from "near-workspaces";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const WASM = fileURLToPath(
  new URL(
    "../reelos-escrow/target/wasm32-unknown-unknown/release/reelos_escrow.wasm",
    import.meta.url,
  ),
);
const PRICE = 100000000000000000000000n;
const STORAGE = 20000000000000000000000n;
const GAS = 100000000000000n;
const digest = "b".repeat(64);

test(
  "compiled escrow executes funding, delivery, settlement, authorization and refund receipts",
  { timeout: 180000 },
  async (t) => {
    const worker = await Worker.init();
    try {
      const root = worker.rootAccount;
      const provider = await root.createSubAccount("studio");
      const client = await root.createSubAccount("client");
      const keylessId = `escrow.${provider.accountId}`;
      const created = await provider
        .batch(keylessId)
        .createAccount()
        .transfer(3n * 10n ** 24n)
        .deployContract(await readFile(WASM))
        .functionCall(
          "new_for_studio",
          { price: PRICE.toString() },
          { gas: GAS },
        )
        .transact();
      assert.equal(created.succeeded, true);
      assert.equal(
        (await root.getAccount(keylessId).view("get_config", {})).provider,
        provider.accountId,
      );
      const keys = await worker.provider.query({
        request_type: "view_access_key_list",
        finality: "final",
        account_id: keylessId,
      });
      assert.equal(
        keys.keys.length,
        0,
        "The wallet-created escrow has no access keys",
      );
      const stranger = await root.createSubAccount("stranger");
      const escrow = await root.createSubAccount("escrow", {
        initialBalance: 5n * 10n ** 24n,
      });
      await escrow.deploy(WASM);
      await escrow.call(
        escrow,
        "new",
        { provider: provider.accountId, price: PRICE.toString() },
        { gas: GAS },
      );
      const config = await escrow.view("get_config", {});
      assert.equal(config.provider, provider.accountId);
      assert.equal(config.price, PRICE.toString());
      const block = await worker.provider.block({ finality: "final" });
      const deadline = (
        BigInt(block.header.timestamp_nanosec) +
        2n * 3600n * 1000000000n
      ).toString();
      const id = "a".repeat(32),
        refundId = "c".repeat(32);
      await client.call(
        escrow,
        "fund_job",
        { job_id: id, brief_hash: digest, deadline_ns: deadline },
        { gas: GAS, attachedDeposit: PRICE + STORAGE },
      );
      assert.equal(
        (await escrow.view("get_job", { job_id: id })).status,
        "funded",
      );
      await assert.rejects(
        stranger.call(
          escrow,
          "deliver_job",
          { job_id: id, delivery_hash: digest },
          { gas: GAS },
        ),
        /Only provider/,
      );
      await assert.rejects(
        client.call(escrow, "refund_job", { job_id: id }, { gas: GAS }),
        /Deadline not reached/,
      );
      await provider.call(
        escrow,
        "deliver_job",
        { job_id: id, delivery_hash: digest },
        { gas: GAS },
      );
      // Settle the provider's previous delivery gas refund before measuring payment.
      await worker.provider.fastForward(5);
      const before = BigInt((await provider.balance()).total);
      await client.call(escrow, "approve_job", { job_id: id }, { gas: GAS });
      assert.equal(
        (await escrow.view("get_job", { job_id: id })).status,
        "paid",
      );
      await worker.provider.fastForward(5);
      const after = BigInt((await provider.balance()).total);
      assert.equal(
        after - before,
        PRICE,
        "Provider receives editing price, not storage deposit",
      );
      await assert.rejects(
        client.call(escrow, "approve_job", { job_id: id }, { gas: GAS }),
        /Job not delivered/,
      );
      await client.call(
        escrow,
        "fund_job",
        { job_id: refundId, brief_hash: digest, deadline_ns: deadline },
        { gas: GAS, attachedDeposit: PRICE + STORAGE },
      );
      await worker.provider.fastForward(15000);
      await client.call(
        escrow,
        "refund_job",
        { job_id: refundId },
        { gas: GAS },
      );
      assert.equal(
        (await escrow.view("get_job", { job_id: refundId })).status,
        "refunded",
      );
      t.diagnostic(
        "Actual Wasm, local node transactions and asynchronous transfer callbacks passed; no public testnet funds used.",
      );
    } finally {
      await worker.tearDown();
    }
  },
);
