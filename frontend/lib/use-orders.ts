"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { api, post } from "./api";
import type { Project } from "./api";
import { orderCall } from "./near-orders";
import type { ChainJob, NearConfig, Order, OrderAction } from "./near-orders";
import { connectWallet, disconnectWallet, signOrder } from "./near-wallet";

async function readChain(id: string) {
  const r = await fetch(`/api/near/jobs/${id}`, { cache: "no-store" });
  if (r.status === 404)
    return {
      job: null as ChainJob | null,
      block_height: null as number | null,
    };
  const body = await r.json();
  if (!r.ok)
    throw new Error(
      body.error?.message ||
        "Cannot verify payment. Refresh before signing again.",
    );
  return body as { job: ChainJob; block_height: number };
}
export function useOrders() {
  const [config, setConfig] = useState<NearConfig>();
  const [projects, setProjects] = useState<Project[]>([]);
  const [project, setProject] = useState<Project>();
  const [history, setHistory] = useState<
    Array<{ id: string; created_at: number; instruction: string }>
  >([]);
  const [order, setOrder] = useState<Order>();
  const [chain, setChain] = useState<ChainJob | null>(null);
  const [verified, setVerified] = useState(false);
  const [block, setBlock] = useState<number | null>(null);
  const [account, setAccount] = useState("");
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [now, setNow] = useState(Date.now());
  const operation = useRef(false);
  const requestId = useRef("");
  const requestSignature = useRef("");
  const revision = useRef(0);
  const refresh = useCallback(async (pid: string, id: string) => {
    const rev = ++revision.current;
    setVerified(false);
    const [local, onchain] = await Promise.all([
      api<Order>(`/projects/${pid}/orders/${id}`),
      readChain(id),
    ]);
    if (rev !== revision.current) return;
    setOrder(local);
    setChain(onchain.job);
    setBlock(onchain.block_height);
    setVerified(true);
  }, []);
  const run = async (label: string, fn: () => Promise<void>) => {
    if (operation.current) return;
    operation.current = true;
    setBusy(label);
    setError("");
    setNotice("");
    try {
      await fn();
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "The request could not finish. Try again.",
      );
    } finally {
      operation.current = false;
      setBusy("");
    }
  };
  const load = useCallback(async () => {
    setError("");
    try {
      const [cfg, rows] = await Promise.all([
        api<NearConfig>("/near/config"),
        api<Project[]>("/projects"),
      ]);
      setConfig(cfg);
      setProjects(rows);
      const params = new URLSearchParams(window.location.search);
      const pid = params.get("project"),
        id = params.get("order");
      if (pid && /^[a-f0-9]{32}$/.test(pid)) {
        setProject(await api<Project>(`/projects/${pid}`));
        setHistory(await api(`/projects/${pid}/orders`));
        if (id && /^[a-f0-9]{32}$/.test(id)) await refresh(pid, id);
      }
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Cannot load the studio. Try again.",
      );
    }
  }, [refresh]);
  useEffect(() => {
    void load();
  }, [load]);
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, []);
  useEffect(() => {
    if (!order || !config?.enabled) return;
    const timer = setInterval(() => {
      void refresh(order.project_id, order.id).catch((e) =>
        setError(e.message),
      );
    }, 6000);
    return () => clearInterval(timer);
  }, [order?.id, order?.project_id, config?.enabled, refresh]);
  const select = (id: string) =>
    run("Loading footage…", async () => {
      setProject(await api<Project>(`/projects/${id}`));
      setHistory(await api(`/projects/${id}/orders`));
      requestId.current = "";
    });
  const connect = () =>
    run("Opening Meteor…", async () => {
      if (!config?.contract_id)
        throw new Error("The testnet contract is not deployed yet.");
      setAccount(await connectWallet(config.contract_id));
    });
  const disconnect = () =>
    run("Disconnecting…", async () => {
      await disconnectWallet();
      setAccount("");
    });
  const create = (asset: string, instruction: string, subject: string) =>
    run("Preparing your order…", async () => {
      if (!project || !account)
        throw new Error("Choose footage and connect a wallet first.");
      const signature = JSON.stringify([
        project.id,
        account,
        asset,
        instruction.trim(),
        subject.trim(),
      ]);
      if (!requestId.current || requestSignature.current !== signature) {
        requestId.current = crypto.randomUUID().replaceAll("-", "");
        requestSignature.current = signature;
      }
      const value = await post<Order>(`/projects/${project.id}/orders`, {
        id: requestId.current,
        client: account,
        asset_id: asset,
        instruction: instruction.trim(),
        subject_prompt: subject.trim(),
      });
      window.history.replaceState(
        null,
        "",
        `/orders?project=${project.id}&order=${value.id}`,
      );
      setOrder(value);
      setHistory(await api(`/projects/${project.id}/orders`));
      await refresh(project.id, value.id);
    });
  const transact = (action: OrderAction) =>
    run("Waiting for wallet…", async () => {
      if (!order || !verified || config?.contract_id !== order.contract_id)
        throw new Error("Refresh the job before signing.");
      // Read again immediately before constructing the wallet request.
      const [fresh, terms] = await Promise.all([
        readChain(order.id),
        api<NearConfig>("/near/config"),
      ]);
      setConfig(terms);
      if (
        !terms.enabled ||
        terms.contract_id !== order.contract_id ||
        terms.config?.provider !== order.config.provider ||
        terms.config?.price !== order.config.price ||
        terms.config?.storage_fee !== order.config.storage_fee
      )
        throw new Error(
          "Studio terms changed. Do not sign this order; prepare a new one.",
        );
      const call = orderCall(action, order, fresh.job, account);
      try {
        await signOrder(call, account);
      } catch {
        setVerified(false);
        throw new Error(
          "Wallet request did not complete. It may have been submitted. Refresh status before retrying.",
        );
      }
      setBusy("Checking finalized status…");
      await refresh(order.project_id, order.id);
      setNotice(
        "Wallet request completed. Finalized contract status is shown below; refresh if it has not updated yet.",
      );
    });
  const start = () =>
    run("Starting your edit…", async () => {
      if (!order) return;
      await post(`/projects/${order.project_id}/orders/${order.id}/start`, {});
      await refresh(order.project_id, order.id);
    });
  const check = () =>
    run("Checking status…", async () => {
      if (order) await refresh(order.project_id, order.id);
      else await load();
    });
  const reset = () => {
    revision.current++;
    setOrder(undefined);
    setChain(null);
    setVerified(false);
    requestId.current = "";
    setError("");
    setNotice("");
    window.history.replaceState(
      null,
      "",
      project ? `/orders?project=${project.id}` : "/orders",
    );
  };
  return {
    config,
    projects,
    project,
    history,
    order,
    chain,
    verified,
    block,
    account,
    busy,
    error,
    notice,
    now,
    select,
    connect,
    disconnect,
    create,
    transact,
    start,
    check,
    reset,
  };
}
