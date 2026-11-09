import { type Effect, type Version, time } from "../lib/api";
import { timelineLanes } from "../lib/timeline-lanes";
import { Icon } from "./icons";

const labels: Record<string, string> = {
  behind_subject_text: "Headline",
  subject_spotlight: "Spotlight",
  tracked_label: "Tracked label",
  graphic_insert: "Illustration",
  footage_insert: "B-roll video",
  trip_shot: "Shot",
  montage_shot: "Shot",
};
export function effectLabel(effect: Effect) {
  return effect.type === "catalog_effect"
    ? String(effect.params.fx || "Effect")
        .replaceAll("-", " ")
        .replace(/\b\w/g, (c) => c.toUpperCase())
    : labels[effect.type] || "Effect";
}
const reelKinds = new Set(["montage", "trip"]);
export function Timeline({
  version,
  playhead,
  selectedId,
  onSeek,
  onSelect,
}: {
  version?: Version;
  playhead: number;
  selectedId?: string;
  onSeek: (time: number) => void;
  onSelect: (effect: Effect, trigger: HTMLElement) => void;
}) {
  const duration = version
    ? version.plan.source_out - version.plan.source_in
    : 30;
  const lanes = timelineLanes(version?.plan.effects || []);
  const isReel = reelKinds.has(version?.kind || "");
  if (!version)
    return (
      <section className="timeline" aria-label="Edit timeline">
        <div className="timeline-heading">
          <h2>Your edit</h2>
          <span>Footage → direction → preview</span>
        </div>
        <p className="timeline-hint">
          Your moments appear here once you generate an edit.
        </p>
      </section>
    );
  return (
    <section className="timeline" aria-label="Edit timeline">
      <div className="timeline-heading">
        <h2>Your edit</h2>
        {version && (
          <select
            aria-label="Select an edit moment"
            value={selectedId || ""}
            onChange={(e) => {
              const effect = version.plan.effects.find(
                (item) => item.id === e.target.value,
              );
              if (effect) {
                onSeek(effect.start);
                onSelect(effect, e.currentTarget);
              }
            }}
          >
            <option value="" disabled>
              Select a moment
            </option>
            {version.plan.effects.map((effect) => (
              <option key={effect.id} value={effect.id}>
                {time(effect.start)} · {effectLabel(effect)}
              </option>
            ))}
          </select>
        )}
        <span>
          {version
            ? `${version.plan.effects.length} moments · ${time(duration)}`
            : "Your moments will appear here"}
        </span>
      </div>
      <div className="ruler mono">
        {[0, 0.25, 0.5, 0.75, 1].map((n) => (
          <span key={n}>{time(duration * n)}</span>
        ))}
      </div>
      <div className="timeline-tracks">
        <button
          className="source-track"
          disabled={!version}
          onClick={() => onSeek(0)}
          aria-label="Go to the start of the edited video"
        >
          <Icon name="film" size={14} />
          <span>
            {isReel
              ? `${version.plan.effects.length} clips`
              : "Source recording"}
          </span>
          <small>{isReel ? "Music + natural sound" : "Original speech"}</small>
        </button>
        {lanes.map((lane, i) => (
          <div
            className="effect-lane"
            key={i}
            aria-label={`Effect track ${i + 1}`}
          >
            {lane.map((effect) => (
              <button
                key={effect.id}
                className={`moment color-${i % 3} ${effect.id === selectedId ? "selected" : ""}`}
                style={{
                  left: `${(effect.start / duration) * 100}%`,
                  width: `${((effect.end - effect.start) / duration) * 100}%`,
                }}
                aria-label={`${effectLabel(effect)}, ${effect.start.toFixed(1)} to ${effect.end.toFixed(1)} seconds`}
                aria-pressed={selectedId === effect.id}
                title={`${effectLabel(effect)} · ${effect.start.toFixed(1)}–${effect.end.toFixed(1)}s`}
                onClick={(event) => {
                  onSeek(effect.start);
                  onSelect(effect, event.currentTarget);
                }}
              >
                <span>{effectLabel(effect)}</span>
              </button>
            ))}
          </div>
        ))}
        {!lanes.length && (
          <p className="timeline-hint">
            Create an edit, then select a moment to inspect it.
          </p>
        )}
      </div>
      <input
        className="playhead"
        type="range"
        aria-label="Video position"
        min={0}
        max={duration}
        step={0.1}
        value={Math.min(duration, Math.max(0, playhead))}
        disabled={!version}
        onChange={(e) => onSeek(Number(e.target.value))}
      />
    </section>
  );
}
