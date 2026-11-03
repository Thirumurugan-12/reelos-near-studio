import { useState } from "react";
import {
  type Asset,
  type ReelStyle,
  type Version,
  clockTime,
  time,
} from "../lib/api";
import { Icon } from "./icons";

export const reelStyles: {
  id: ReelStyle;
  label: string;
  hint: string;
  times: boolean;
  direction: string;
}[] = [
  {
    id: "calm",
    label: "Calm",
    hint: "Mist dissolves, serif title, unhurried shots",
    times: true,
    direction: "Calm and cinematic. Open on the most atmospheric shot.",
  },
  {
    id: "energetic",
    label: "Energetic",
    hint: "Beat cuts, whips, punch-ins, bold type",
    times: false,
    direction: "Fast and energetic. Lead with the most dynamic moments.",
  },
  {
    id: "clean",
    label: "Clean",
    hint: "Hard cuts, minimal type, fade to black",
    times: true,
    direction: "Simple and clear. Let each moment breathe.",
  },
];

export function reelClips(assets: Asset[]) {
  return assets
    .filter((a) => a.role === "clip")
    .sort((a, b) => (a.recorded_at || "~").localeCompare(b.recorded_at || "~"));
}

export function isReel(version?: Version) {
  return version?.kind === "montage" || version?.kind === "trip";
}

export function reelSettings(version?: Version) {
  const data = version?.montage || version?.trip;
  return {
    style: (data?.style || "calm") as ReelStyle,
    showTimes: data?.show_times ?? true,
  };
}

function StylePicker({
  value,
  onChange,
  disabled,
}: {
  value: ReelStyle;
  onChange: (style: ReelStyle) => void;
  disabled: boolean;
}) {
  return (
    <fieldset className="reel-styles" disabled={disabled}>
      <legend className="field-label">Style</legend>
      <div className="reel-style-grid">
        {reelStyles.map((s) => (
          <button
            key={s.id}
            type="button"
            className={`reel-style ${value === s.id ? "selected" : ""}`}
            aria-pressed={value === s.id}
            onClick={() => onChange(s.id)}
          >
            <strong>{s.label}</strong>
            <span>{s.hint}</span>
          </button>
        ))}
      </div>
    </fieldset>
  );
}

export function ReelPanel({
  clips,
  version,
  busy,
  canPlan,
  onMake,
  onRestyle,
  onAddClips,
}: {
  clips: Asset[];
  version?: Version;
  busy: boolean;
  canPlan: boolean;
  onMake: (
    clipIds: string[],
    title: string,
    direction: string,
    style: ReelStyle,
    showTimes: boolean,
  ) => void;
  onRestyle: (style: ReelStyle, showTimes: boolean) => void;
  onAddClips: () => void;
}) {
  const current = reelSettings(version);
  const hasReel = isReel(version);
  const [style, setStyle] = useState<ReelStyle>(current.style);
  const [showTimes, setShowTimes] = useState(current.showTimes);
  const [title, setTitle] = useState("");
  const [direction, setDirection] = useState(reelStyles[0].direction);
  const [editedDirection, setEditedDirection] = useState(false);
  const total = clips.reduce((sum, clip) => sum + clip.duration, 0);
  const changed = style !== current.style || showTimes !== current.showTimes;

  function pick(next: ReelStyle) {
    const preset = reelStyles.find((s) => s.id === next)!;
    setStyle(next);
    setShowTimes(preset.times);
    if (!editedDirection) setDirection(preset.direction);
  }
  const timesToggle = (
    <label className="checkbox">
      <input
        type="checkbox"
        checked={showTimes}
        onChange={(e) => setShowTimes(e.target.checked)}
        disabled={busy}
      />{" "}
      Show recording times and date
    </label>
  );

  return (
    <section
      className="direction panel reel-panel"
      aria-label="Multi-clip reel"
    >
      <div className="panel-heading">
        <h2>Multi-clip reel</h2>
        <span className="spark-mark">
          <Icon name="sparkle" size={16} />
        </span>
      </div>
      <p className="muted small">
        Muse watches your clips and picks the shots. Times come from your
        camera; every cut lands on the music.
      </p>
      {hasReel && (
        <div className="reel-restyle">
          <StylePicker value={style} onChange={pick} disabled={busy} />
          {timesToggle}
          <button
            className="primary wide"
            disabled={busy || !changed}
            onClick={() => onRestyle(style, showTimes)}
          >
            Apply style <Icon name="arrow" size={14} />
          </button>
          <p className="privacy-note">
            Same shots and captions, re-timed and re-rendered. No new Muse
            request; the current version stays in History.
          </p>
        </div>
      )}
      <details className="reel-new" open={!hasReel}>
        <summary>
          {hasReel ? "Make a new reel with Muse" : "Your clips"}
        </summary>
        <ol className="reel-clips" aria-label="Clips in recording order">
          {clips.map((clip, i) => (
            <li key={clip.id}>
              <span className="reel-index">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="reel-name">{clip.name}</span>
              <span className="reel-meta">
                {clockTime(clip.recorded_at) || "—"} ·{" "}
                {clip.duration < 10
                  ? `${clip.duration.toFixed(1)} s`
                  : time(clip.duration)}
                {clip.duration < 1.5 && " · slow-mo"}
              </span>
            </li>
          ))}
        </ol>
        <p className="reel-total small muted">
          {clips.length} clips · {Math.round(total)} s of footage → a short
          portrait reel
        </p>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onMake(
              clips.map((c) => c.id),
              title.trim(),
              direction.trim() || "A short, well-paced reel.",
              style,
              showTimes,
            );
          }}
        >
          {!hasReel && (
            <>
              <StylePicker value={style} onChange={pick} disabled={busy} />
              {timesToggle}
            </>
          )}
          <label className="field-label" htmlFor="reel-title">
            Title on screen
          </label>
          <input
            id="reel-title"
            value={title}
            maxLength={24}
            placeholder="Optional · leave empty for Muse"
            onChange={(e) => setTitle(e.target.value)}
            disabled={busy}
          />
          <label className="field-label" htmlFor="reel-direction">
            How should it feel?
          </label>
          <textarea
            id="reel-direction"
            value={direction}
            maxLength={2000}
            rows={3}
            onChange={(e) => {
              setDirection(e.target.value);
              setEditedDirection(true);
            }}
            disabled={busy}
          />
          <button
            className={hasReel ? "secondary wide" : "primary wide"}
            disabled={busy || !canPlan || clips.length < 2}
          >
            Make reel <Icon name="arrow" size={14} />
          </button>
          <p className="privacy-note">
            One Muse request (counted in your local allowance). Rendered with
            HyperFrames. Your clips stay unchanged.
          </p>
        </form>
        <button className="text-button" onClick={onAddClips} disabled={busy}>
          Add more clips →
        </button>
      </details>
    </section>
  );
}
