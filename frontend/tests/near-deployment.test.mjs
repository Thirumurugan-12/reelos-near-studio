import test from "node:test";
import assert from "node:assert/strict";
import { reviewDeployment } from "../lib/near-deployment.ts";
const wasm = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0]);
const hash = Buffer.from(await crypto.subtle.digest("SHA-256", wasm)).toString(
  "hex",
);
const manifest = {
  network: "testnet",
  deposit: "3000000000000000000000000",
  price: "100000000000000000000000",
  storage_fee: "20000000000000000000000",
  wasm_bytes: 8,
  wasm_sha256: hash,
  initializer: "new_for_studio",
};
test("review binds the named testnet wallet to a three-NEAR keyless subaccount", async () => {
  const plan = await reviewDeployment(manifest, "studio.testnet", wasm);
  assert.equal(plan.receiverId, "escrow.studio.testnet");
  assert.equal(plan.deposit, "3000000000000000000000000");
  assert.equal(plan.initializer, "new_for_studio");
});
test("deployment rejects unexpected network, pricing and altered Wasm", async () => {
  await assert.rejects(
    reviewDeployment(
      { ...manifest, network: "mainnet" },
      "studio.testnet",
      wasm,
    ),
  );
  await assert.rejects(
    reviewDeployment(
      { ...manifest, deposit: "4000000000000000000000000" },
      "studio.testnet",
      wasm,
    ),
  );
  await assert.rejects(reviewDeployment(manifest, "studio.near", wasm));
  await assert.rejects(
    reviewDeployment(
      { ...manifest, wasm_sha256: "a".repeat(64) },
      "studio.testnet",
      wasm,
    ),
  );
});
