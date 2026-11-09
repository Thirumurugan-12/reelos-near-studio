export type DeploymentManifest = {
  network: string;
  wallet_deployment: false;
  deposit: string;
  price: string;
  storage_fee: string;
  wasm_bytes: number;
  wasm_sha256: string;
};
