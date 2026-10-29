import { type Asset, type Version, time } from "../lib/api";
import { Icon } from "./icons";

export function Preview({
  projectId,
  source,
  version,
  original,
  onOriginal,
  busy,
}: {
  projectId?: string;
  source?: Asset;
  version?: Version;
  original: boolean;
  onOriginal: (value: boolean) => void;
  busy: boolean;
}) {
  const hasEdit = !!version?.has_preview;
  const src =
    projectId && (original || !hasEdit) && source
      ? `/api/projects/${projectId}/assets/${source.id}/source`
      : projectId && hasEdit
        ? `/api/projects/${projectId}/versions/${version!.id}/preview`
        : undefined;
  return (
    <section className="preview-area" aria-label="Video preview">
      <div className="stage-toolbar">
        <span className="eyebrow">THE PREVIEW</span>
        <div className="segmented" aria-label="Compare original and edit">
          <button
            onClick={() => onOriginal(true)}
            aria-pressed={original || !hasEdit}
            disabled={!source}
          >
            Original
          </button>
          <button
            onClick={() => onOriginal(false)}
            aria-pressed={!original && hasEdit}
            disabled={!hasEdit}
          >
            Edit
          </button>
        </div>
      </div>
      <div className="video-stage">
        {src ? (
          <video
            key={src}
            src={src}
            controls
            playsInline
            preload="metadata"
            aria-label={
              original || !hasEdit ? "Original footage" : "Edited video"
            }
          />
        ) : (
          <div className="stage-empty">
            <span className="empty-frame">
              <Icon name="film" size={36} />
            </span>
            <h2>
              Your next great edit
              <br />
              starts here.
            </h2>
            <p>
              Bring your footage.
              <br />
              We’ll help it find its form.
            </p>
            <span className="stage-format">PORTRAIT · 9:16</span>
          </div>
        )}
        {busy && (
          <span className="working-badge">
            <span className="activity-dot" /> Working on your edit
          </span>
        )}
      </div>
      <div className="preview-caption">
        <span>
          <Icon name="film" size={14} />{" "}
          {src
            ? original || !hasEdit
              ? "Source footage"
              : "Edited preview"
            : "Your canvas is ready"}
        </span>
        <span>
          {source
            ? time(
                original || !hasEdit
                  ? source.duration
                  : version!.plan.source_out - version!.plan.source_in,
              )
            : "15–30s"}{" "}
          <span className="divider">/</span>{" "}
          {original || !hasEdit ? "Original" : "360p preview"}
        </span>
      </div>
    </section>
  );
}
