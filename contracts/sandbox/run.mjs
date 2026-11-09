import { Binary } from "near-sandbox";
import { homedir } from "node:os";
import { join, dirname } from "node:path";
import { spawnSync } from "node:child_process";

// Match the public testnet runtime checked on 9 November 2026.
const version = "2.14.0-rc.5";
const platform =
  process.platform === "darwin" && process.arch === "arm64"
    ? "Darwin-arm64"
    : process.platform === "linux" && process.arch === "x64"
      ? "Linux-x86_64"
      : null;
if (!platform)
  throw new Error(
    "Sandbox requires Apple Silicon macOS or Linux x64 for this pinned runtime.",
  );
const location =
  process.env.NEAR_SANDBOX_BIN_PATH ||
  join(homedir(), ".local/share", `reelos-sandbox-${version}`, platform);
const url = `https://s3-us-west-1.amazonaws.com/build.nearprotocol.com/nearcore/${platform}/${version}/near-sandbox.tar.gz`;
const binary = await Binary.create("near-sandbox", url, location);
if (!(await binary.exists())) await binary.install();
const check = spawnSync(binary.binPath, ["--version"], { encoding: "utf8" });
if (check.status !== 0 || !check.stdout.includes(version))
  throw new Error("The Sandbox binary does not match the pinned runtime.");
console.log(check.stdout.trim());
const outcome = spawnSync(
  process.execPath,
  ["--test", "--test-concurrency=1", "escrow.test.mjs"],
  {
    cwd: dirname(new URL(import.meta.url).pathname),
    stdio: "inherit",
    env: {
      ...process.env,
      NEAR_SANDBOX_BIN_PATH: location,
      NEAR_SANDBOX_BINARY_PATH: location,
    },
  },
);
process.exitCode = outcome.status ?? 1;
