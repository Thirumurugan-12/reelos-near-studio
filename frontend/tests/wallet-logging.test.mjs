import test from "node:test";
import assert from "node:assert/strict";
import {
  mkdtemp,
  mkdir,
  copyFile,
  writeFile,
  readFile,
  rm,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

test("wallet logging guard removes generated key diagnostics and is repeatable", async () => {
  const root = await mkdtemp(join(tmpdir(), "reelos-sdk-guard-"));
  try {
    await mkdir(join(root, "scripts"));
    await copyFile(
      new URL("../scripts/patch-meteor-sdk.mjs", import.meta.url),
      join(root, "scripts/patch.mjs"),
    );
    const sdk = join(root, "node_modules/@meteorwallet/sdk");
    await mkdir(join(sdk, "dist"), { recursive: true });
    await mkdir(join(sdk, "src"));
    await writeFile(
      join(sdk, "package.json"),
      JSON.stringify({ version: "1.0.24" }),
    );
    for (const path of ["dist/index.js", "src/MeteorWallet.ts"])
      await writeFile(
        join(sdk, path),
        "const accessKey = makeKey(); console.log(accessKey);\n",
      );
    for (let i = 0; i < 2; i++)
      assert.equal(
        spawnSync(process.execPath, [join(root, "scripts/patch.mjs")]).status,
        0,
      );
    const patched = await readFile(join(sdk, "dist/index.js"), "utf8");
    assert.ok(!patched.includes("console.log(accessKey)"));
    assert.ok(patched.includes("const accessKey = makeKey()"));
    await writeFile(
      join(sdk, "package.json"),
      JSON.stringify({ version: "2.0.0" }),
    );
    assert.notEqual(
      spawnSync(process.execPath, [join(root, "scripts/patch.mjs")]).status,
      0,
    );
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});
