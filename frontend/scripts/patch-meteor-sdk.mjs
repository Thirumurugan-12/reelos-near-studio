// The pinned Meteor SDK logs a generated signing key during requestSignIn.
// Remove that diagnostic before bundling; fail closed when the dependency changes.
import { readFile, writeFile } from "node:fs/promises";
const base = new URL("../node_modules/@meteorwallet/sdk/", import.meta.url);
const pkg = JSON.parse(await readFile(new URL("package.json", base), "utf8"));
if (pkg.version !== "1.0.24")
  throw new Error(
    "Review the wallet logging patch for the new Meteor SDK version.",
  );
const marker = "/* ReelOS: never log generated wallet signing keys. */";
for (const name of ["dist/index.js", "src/MeteorWallet.ts"]) {
  const path = new URL(name, base);
  const original = await readFile(path, "utf8");
  if (original.includes("console.log(accessKey);")) {
    await writeFile(
      path,
      original.replaceAll("console.log(accessKey);", marker),
    );
  } else if (!original.includes(marker)) {
    throw new Error(`Wallet logging patch could not be verified in ${name}`);
  }
}
