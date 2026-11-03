export type Asset = {
  id: string;
  name: string;
  role: "source" | "reference" | "supporting" | "clip";
  kind?: "image" | "video";
  recorded_at?: string | null;
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
  params: { text?: string; fx?: string };
};
export type Plan = {
  framing?: { scale: number; offset_y: number };
  asset_id: string;
  source_in: number;
  source_out: number;
  effects: Effect[];
};
export type Version = {
  id: string;
  kind?: "montage" | "trip";
  montage?: ReelPlan;
  carousel?: { slides: string[]; style?: string; model?: string };
  render_profile?: { broll_art?: string };
  trip?: ReelPlan;
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
  observations: {
    text: string;
    origin: string;
    source_start?: number | null;
    source_end?: number | null;
    timing?: "approximate" | "unverified";
  }[];
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
  request: { asset_id?: string; subject_prompt?: string };
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
export type UploadRole = Asset["role"];
export type ReelStyle = "calm" | "energetic" | "clean";
export type ReelPlan = {
  title: string;
  style?: ReelStyle;
  show_times?: boolean;
  shots: { clip_id: string; slow: boolean }[];
};

/** Local wall-clock time from a clip's recording timestamp, e.g. "07:23". */
export function clockTime(iso?: string | null) {
  const match = iso?.match(/T(\d{2}):(\d{2})/);
  return match ? `${match[1]}:${match[2]}` : "";
}
export function time(seconds: number) {
  return `${Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0")}:${Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0")}`;
}

export type CatalogParams = {
  fx: string;
  text: string;
  options: Record<string, string | number>;
  media_ids: string[];
};
export type CatalogItem = {
  id: string;
  label: string;
  description: string;
  options: string[];
  numeric_options: Record<string, [number, number]>;
  enum_options: Record<string, string[]>;
  preview_url: string;
  poster_url: string;
  preview_ready: boolean;
  multiline_text: boolean;
  accepts_text: boolean;
  uses_media: boolean;
  example: CatalogParams;
  looks: string[];
  requires_values: boolean;
};
