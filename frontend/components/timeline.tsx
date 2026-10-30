import { type Version, time } from "../lib/api";
import { Icon } from "./icons";

const labels: Record<string, string> = {
  behind_subject_text: "Headline",
  subject_spotlight: "Spotlight",
  tracked_label: "Tracked label",
  graphic_insert: "Graphic insert",
};
export function Timeline({ version }: { version?: Version }) {
  const duration = version
    ? version.plan.source_out - version.plan.source_in
    : 30;
  return (
    <section className="timeline panel" aria-label="Effects timeline">
      <div className="panel-heading">
        <h2>
          <Icon name="layers" size={16} /> Edit overview
        </h2>
        <span className="small muted">
          {version
            ? `${version.plan.effects.length} effects · ${time(duration)}`
            : "Your decisions, on a timeline"}
        </span>
      </div>
      <div className="ruler">
        <span>00:00</span>
        <span>{time(duration / 3)}</span>
        <span>{time((duration * 2) / 3)}</span>
        <span>{time(duration)}</span>
      </div>
      {version ? (
        <div className="tracks">
          {version.plan.effects.map((effect, i) => (
            <div className="track" key={effect.id}>
              <span className="track-label">
                {labels[effect.type] || effect.type}
              </span>
              <div className="track-line">
                <div
                  className={`effect-block color-${i % 3}`}
                  style={{
                    left: `${(effect.start / duration) * 100}%`,
                    width: `${((effect.end - effect.start) / duration) * 100}%`,
                  }}
                  title={`${effect.reason} (${effect.start.toFixed(1)}–${effect.end.toFixed(1)}s)`}
                >
                  <span>{effect.params.text || labels[effect.type]}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="timeline-empty">
          <span />
          <p>Your storyboard and effects will appear after the first draft.</p>
        </div>
      )}
    </section>
  );
}
