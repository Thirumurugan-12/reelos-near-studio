import { type RefObject } from "react";
import { type Asset, type Version, time } from "../lib/api";
import { Icon } from "./icons";

export function Preview({
  projectId,
  source,
  version,
  original,
  onOriginal,
  busy,
  videoRef,
  onTimeChange,
  onAddFootage,
}: {
  projectId?: string;
  source?: Asset;
  version?: Version;
  original: boolean;
  onOriginal: (value: boolean) => void;
  busy: boolean;
  videoRef: RefObject<HTMLVideoElement | null>;
  onTimeChange: (time: number) => void;
  onAddFootage: () => void;
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
        <span className="eyebrow">PREVIEW · 9:16</span>
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
            ref={videoRef}
            onTimeUpdate={(e) => onTimeChange(e.currentTarget.currentTime)}
            onLoadedMetadata={(e) => onTimeChange(e.currentTarget.currentTime)}
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
              Start with
              <br />
              your story.
            </h2>
            <p>
              Upload a recording, give it a direction,
              <br />
              and make the edit your own.
            </p>
            <button className="primary" onClick={onAddFootage}>
              Add your footage <Icon name="arrow" size={16} />
            </button>
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
            : "9:16"}{" "}
          <span className="divider">/</span>{" "}
          {original || !hasEdit ? "Original" : "360p preview"}
        </span>
      </div>
    </section>
  );
}
