import { type RefObject } from "react";
import { type Project, type Version } from "../lib/api";
import { Icon } from "./icons";

export function VersionHistory({
  project,
  version,
  busy,
  dialogRef,
  onSelect,
  onRestore,
}: {
  project: Project | null;
  version?: Version;
  busy: boolean;
  dialogRef: RefObject<HTMLDialogElement | null>;
  onSelect: (id: string) => void;
  onRestore: () => void;
}) {
  const prefix = project ? `/api/projects/${project.id}` : "";
  return (
    <dialog
      ref={dialogRef}
      className="history-dialog"
      aria-labelledby="history-title"
    >
      <div className="dialog-heading">
        <div>
          <span className="eyebrow">YOUR PROJECT</span>
          <h2 id="history-title">Version history</h2>
        </div>
        <button
          className="icon-button"
          aria-label="Close version history"
          onClick={() => dialogRef.current?.close()}
        >
          ×
        </button>
      </div>
      <p className="muted small">
        Preview an earlier direction. Every version keeps its own edit.
      </p>
      <div className="version-list">
        {project?.versions.map((v, i) => (
          <button
            key={v.id}
            disabled={busy}
            aria-pressed={v.id === version?.id}
            className={v.id === version?.id ? "selected" : ""}
            onClick={() => {
              onSelect(v.id);
              dialogRef.current?.close();
            }}
          >
            <span className="version-number mono">
              v{project!.versions.length - i}
            </span>
            <span>
              <strong>{v.summary}</strong>
              <small>
                {v.has_export
                  ? "1080p export ready"
                  : v.has_preview
                    ? "Preview ready"
                    : "Storyboard"}
                {v.id === project?.current_version_id ? " · Current" : ""}
              </small>
            </span>
            {v.id === version?.id && <Icon name="check" size={16} />}
          </button>
        ))}
      </div>
      {!project?.versions.length && (
        <p>No versions yet. Add footage and generate your first preview.</p>
      )}
      {version && (
        <div className="history-actions">
          {version.has_preview &&
            project?.current_version_id !== version.id && (
              <button className="primary" onClick={onRestore} disabled={busy}>
                Restore selected version <Icon name="arrow" size={14} />
              </button>
            )}
          <a href={`${prefix}/versions/${version.id}/plan`}>
            Download editing plan ↗
          </a>
          {version.has_export && (
            <a href={`${prefix}/versions/${version.id}/export`}>
              Download 1080p MP4 ↗
            </a>
          )}
        </div>
      )}
    </dialog>
  );
}
