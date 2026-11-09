export type DeploymentManifest = {
  network: string;
  deposit: string;
  price: string;
  storage_fee: string;
  wasm_bytes: number;
  wasm_sha256: string;
  initializer: string;
};
export async function reviewDeployment(
  manifest: DeploymentManifest,
  studio: string,
  wasm: Uint8Array,
) {
  const receiverId = `escrow.${studio}`;
  const named = /^(([a-z0-9]+[-_])*[a-z0-9]+\.)*([a-z0-9]+[-_])*[a-z0-9]+$/;
  if (
    manifest.network !== "testnet" ||
    !studio.endsWith(".testnet") ||
    !named.test(studio) ||
    receiverId.length > 64
  )
    throw new Error("Use a named NEAR testnet account to create your escrow.");
  if (
    manifest.deposit !== "3000000000000000000000000" ||
    manifest.price !== "100000000000000000000000" ||
    manifest.storage_fee !== "20000000000000000000000" ||
    manifest.initializer !== "new_for_studio"
  )
    throw new Error("Deployment terms differ from the reviewed 3 NEAR setup.");
  if (
    wasm.length !== manifest.wasm_bytes ||
    wasm.length > 290000 ||
    wasm.length < 8 ||
    wasm[0] !== 0 ||
    wasm[1] !== 97 ||
    wasm[2] !== 115 ||
    wasm[3] !== 109
  )
    throw new Error(
      "Unexpected contract artifact. Rebuild and review before signing.",
    );
  const sha = await crypto.subtle.digest("SHA-256", new Uint8Array(wasm));
  const digest = Array.from(new Uint8Array(sha), (n) =>
    n.toString(16).padStart(2, "0"),
  ).join("");
  if (digest !== manifest.wasm_sha256)
    throw new Error("Contract artifact changed. Refresh before signing.");
  return {
    receiverId,
    deposit: manifest.deposit,
    price: manifest.price,
    initializer: manifest.initializer,
  };
}
