"use client";

import { useCallback, useEffect, useState } from "react";
import {
  api,
  post,
  type Asset,
  type Health,
  type Job,
  type Project,
} from "./api";

export function useStudio() {
  const [health, setHealth] = useState<Health | null>(null);
  const [projects, setProjects] = useState<{ id: string; name: string }[]>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [versionId, setVersionId] = useState("");
  const [sourceId, setSourceId] = useState("");
  const [referenceId, setReferenceId] = useState("");
  const [job, setJob] = useState<Job | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [reserved, setReserved] = useState(0);
  const [limit, setLimit] = useState(150);

  const load = useCallback(async (id: string) => {
    const next = await api<Project>(`/projects/${id}`);
    setProject(next);
    return next;
  }, []);
  const refreshUsage = useCallback(async () => {
    const usage = await api<{ reserved_usd: number; limit_usd: number }>(
      "/usage",
    );
    setReserved(usage.reserved_usd);
    setLimit(usage.limit_usd);
  }, []);
  useEffect(() => {
    Promise.all([
      api<Health>("/health"),
      api<{ id: string; name: string }[]>("/projects"),
    ])
      .then(async ([h, list]) => {
        setHealth(h);
        setProjects(list);
        const id = new URLSearchParams(window.location.search).get("project");
        if (id && list.some((p) => p.id === id)) {
          const p = await load(id);
          setVersionId(p.current_version_id || "");
          setSourceId(p.assets.find((a) => a.role === "source")?.id || "");
          setReferenceId(
            p.assets.find((a) => a.role === "reference")?.id || "",
          );
          setJob(
            p.jobs.find((j) => ["queued", "running"].includes(j.status)) ||
              p.jobs[0] ||
              null,
          );
        }
        await refreshUsage();
      })
      .catch((e) => setError(e.message));
  }, [load, refreshUsage]);

  const running = !!job && ["queued", "running"].includes(job.status);
  useEffect(() => {
    if (!running || !project || !job) return;
    let stopped = false;
    const tick = async () => {
      try {
        const next = await api<Job>(`/projects/${project.id}/jobs/${job.id}`);
        if (stopped) return;
        setJob(next);
        if (!["queued", "running"].includes(next.status)) {
          await load(project.id);
          if (next.version_id) setVersionId(next.version_id);
          if (next.error) setError(next.error);
          await refreshUsage();
        }
      } catch (e) {
        if (!stopped) setError((e as Error).message);
      }
    };
    const timer = setInterval(tick, 1200);
    return () => {
      stopped = true;
      clearInterval(timer);
    };
  }, [running, project?.id, job?.id, load, refreshUsage]);

  async function attempt<T>(fn: () => Promise<T>): Promise<T | undefined> {
    setBusy(true);
    setError("");
    try {
      return await fn();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function create() {
    return attempt(async () => {
      const p = await post<Project>("/projects", {
        name: `Untitled reel ${projects.length + 1}`,
      });
      const full = await load(p.id);
      setProjects((prev) => [p, ...prev]);
      setVersionId("");
      setSourceId("");
      setReferenceId("");
      setJob(null);
      setSubjectId("");
      window.history.replaceState(null, "", `?project=${p.id}`);
      return full;
    });
  }
  async function select(id: string) {
    await attempt(async () => {
      const p = await load(id);
      setVersionId(p.current_version_id || "");
      setSourceId(p.assets.find((a) => a.role === "source")?.id || "");
      setReferenceId(p.assets.find((a) => a.role === "reference")?.id || "");
      setJob(
        p.jobs.find((j) => ["queued", "running"].includes(j.status)) ||
          p.jobs[0] ||
          null,
      );
      setSubjectId("");
      window.history.replaceState(null, "", `?project=${id}`);
    });
  }
  async function upload(file: File, role: "source" | "reference") {
    await attempt(async () => {
      let p = project;
      if (!p) {
        const record = await post<Project>("/projects", {
          name: file.name.replace(/\.[^.]+$/, ""),
        });
        p = await load(record.id);
        setProjects((prev) => [record, ...prev]);
        window.history.replaceState(null, "", `?project=${p.id}`);
      }
      const form = new FormData();
      form.set("file", file);
      form.set("role", role);
      const asset = await api<Asset>(`/projects/${p.id}/assets`, {
        method: "POST",
        body: form,
      });
      if (role === "source") {
        setSourceId(asset.id);
        setVersionId("");
      } else {
        setReferenceId(asset.id);
      }
      setSubjectId("");
      setJob(null);
      await load(p.id);
    });
  }
  async function start(data: Record<string, unknown>) {
    if (!project) return;
    await attempt(async () => {
      const next = await post<Job>(`/projects/${project.id}/jobs`, data);
      setJob(next);
    });
  }
  async function restore() {
    if (!project || !versionId) return;
    await attempt(async () => {
      await post(`/projects/${project.id}/versions/${versionId}/restore`, {});
      await load(project.id);
    });
  }
  function selectSource(id: string) {
    setSourceId(id);
    setVersionId("");
    setSubjectId("");
    setJob(null);
  }
  return {
    health,
    projects,
    project,
    versionId,
    setVersionId,
    sourceId,
    setSourceId: selectSource,
    referenceId,
    setReferenceId,
    job,
    busy: busy || running,
    error,
    setError,
    subjectId,
    setSubjectId,
    reserved,
    limit,
    create,
    select,
    upload,
    start,
    restore,
  };
}
