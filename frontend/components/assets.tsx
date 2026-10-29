import { type Asset, time } from "../lib/api";
import { Icon } from "./icons";

export function Assets({
  assets,
  sourceId,
  referenceId,
  onSource,
  onReference,
  onUpload,
  disabled,
}: {
  assets: Asset[];
  sourceId: string;
  referenceId: string;
  onSource: (id: string) => void;
  onReference: (id: string) => void;
  onUpload: (file: File, role: "source" | "reference") => void;
  disabled: boolean;
}) {
  return (
    <aside className="assets panel" aria-label="Project assets">
      <div className="panel-heading">
        <h2>Your footage</h2>
        <span className="count">
          {assets.filter((a) => a.role === "source").length}
        </span>
      </div>
      <p className="muted small">The raw material. You bring the story.</p>
      <label className={`upload-box ${disabled ? "disabled" : ""}`}>
        <input
          type="file"
          accept="video/mp4,video/quicktime,.mov"
          disabled={disabled}
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onUpload(f, "source");
            e.target.value = "";
          }}
        />
        <Icon name="upload" />
        <strong>Upload footage</strong>
        <span>MP4 or MOV · up to 60 seconds</span>
      </label>
      <div className="asset-list">
        {assets
          .filter((a) => a.role === "source")
          .map((asset) => (
            <button
              key={asset.id}
              className={`asset-item ${asset.id === sourceId ? "selected" : ""}`}
              onClick={() => onSource(asset.id)}
              disabled={disabled}
              aria-pressed={asset.id === sourceId}
            >
              <span className="asset-icon">
                <Icon name="film" />
              </span>
              <span>
                <strong>{asset.name}</strong>
                <small>
                  {time(asset.duration)} · {asset.width} × {asset.height}
                </small>
              </span>
              {asset.id === sourceId && <Icon name="check" size={16} />}
            </button>
          ))}
      </div>
      <div className="reference-section">
        <div className="panel-heading">
          <h2>Style reference</h2>
          <span className="optional">Optional</span>
        </div>
        <p className="muted small">Show us the feeling you have in mind.</p>
        <label className="reference-upload">
          <Icon name="plus" size={16} /> Add reference video
          <input
            type="file"
            accept="video/mp4,video/quicktime,.mov"
            disabled={disabled}
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) onUpload(f, "reference");
              e.target.value = "";
            }}
          />
        </label>
        {assets.some((a) => a.role === "reference") && (
          <select
            aria-label="Style reference"
            value={referenceId}
            disabled={disabled}
            onChange={(e) => onReference(e.target.value)}
          >
            <option value="">No reference</option>
            {assets
              .filter((a) => a.role === "reference")
              .map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
          </select>
        )}
      </div>
      <div className="asset-note">
        <Icon name="layers" size={17} />
        <p>
          Your footage stays original.
          <br />
          Every edit gets its own version.
        </p>
      </div>
    </aside>
  );
}
