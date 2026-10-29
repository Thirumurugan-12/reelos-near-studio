export type Asset = {
  id: string;
  name: string;
  role: "source" | "reference";
  duration: number;
  width: number;
  height: number;
};
export type Effect = {
  id: string;
  type: string;
  start: number;
  end: number;
  subject_id: string;
  reason: string;
  params: { text?: string };
};
export type Plan = {
  asset_id: string;
  source_in: number;
  source_out: number;
  effects: Effect[];
};
export type Version = {
  id: string;
  parent_id: string | null;
  created_at: number;
  plan: Plan;
  summary: string;
  has_preview: boolean;
  has_export: boolean;
  storyboard: {
    operation_id: string;
    type: string;
    start: number;
    end: number;
    reason: string;
    text?: string;
  }[];
  observations: { text: string; origin: string }[];
};
export type Job = {
  id: string;
  status: string;
  stage: string;
  progress: number | null;
  error?: string;
  version_id?: string;
  result?: { subjects: string[]; track_key: string };
  elapsed?: number;
};
export type Project = {
  id: string;
  name: string;
  current_version_id: string | null;
  assets: Asset[];
  versions: Version[];
  jobs: Job[];
};
export type Health = { meta_configured: boolean; status: string };

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, { cache: "no-store", ...init });
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      data.error?.message || "The request could not finish. Try again.",
    );
  return data;
}
export function post<T>(path: string, data: unknown) {
  return api<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}
export function time(seconds: number) {
  return `${Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0")}:${Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0")}`;
}
