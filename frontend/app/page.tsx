"use client";

import { useState } from "react";
import { useStudio } from "../lib/use-studio";
import { Assets } from "../components/assets";
import { Direction } from "../components/direction";
import { Preview } from "../components/preview";
import { Timeline } from "../components/timeline";
import { EffectBrowser } from "../components/effect-browser";
import { Icon } from "../components/icons";

export default function Studio() {
  const s = useStudio();
  const [leftMode, setLeftMode] = useState("assets");
  const [original, setOriginal] = useState(false);
  const [mobileTab, setMobileTab] = useState("preview");
  const version = s.project?.versions.find((v) => v.id === s.versionId);
  const source = s.project?.assets.find(
    (a) => a.id === (version?.plan.asset_id || s.sourceId),
  );
  const prefix = s.project ? `/api/projects/${s.project.id}` : "";
  const draft = (
    instruction: string,
    review: boolean,
    subject: string,
    outputMode: "full" | "reel",
  ) =>
    s.start({
      action: "draft",
      asset_id: s.sourceId,
      reference_id: s.referenceId || null,
      instruction,
      subject_prompt: subject,
      subject_id: s.subjectId || null,
      review_storyboard: review,
      output_mode: outputMode,
    });
  return (
    <main className="studio">
      <header className="app-header">
        <a href="/" className="wordmark" aria-label="ReelOS home">
          <span className="brand-icon">
            <Icon name="film" size={19} />
          </span>
          reel<span>os</span>
          <small>BETA</small>
        </a>
        <div className="project-picker">
          <label className="sr-only" htmlFor="project">
            Project
          </label>
          <select
            id="project"
            value={s.project?.id || ""}
            onChange={(e) => s.select(e.target.value)}
            disabled={s.busy}
          >
            <option value="" disabled>
              Your workspace
            </option>
            {s.projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
          <button
            className="icon-button"
            onClick={s.create}
            disabled={s.busy}
            aria-label="New project"
          >
            <Icon name="plus" />
          </button>
        </div>
        <div className="header-end">
          <span
            className={`connection ${s.health?.meta_configured ? "connected" : ""}`}
          >
            <span />
            {s.health?.meta_configured
              ? "Meta connected"
              : s.health
                ? "Meta key needed"
                : "Connecting"}
          </span>
          <button
            className="primary export-button"
            aria-label="Export video"
            disabled={!version?.has_preview || s.busy}
            onClick={() =>
              s.start({
                action: "render",
                version_id: version!.id,
                quality: "export",
              })
            }
          >
            <Icon name="download" size={16} />
            <span>Export</span>
          </button>
        </div>
      </header>
      <div className="workspace-heading">
        <div>
          <span className="eyebrow">YOUR CREATIVE STUDIO</span>
          <h1>{s.project?.name || "Good footage. Great possibilities."}</h1>
        </div>
        <p>Make something worth watching.</p>
      </div>
      {s.error && (
        <div className="error-banner" role="alert">
          <span>{s.error}</span>
          <button onClick={() => s.setError("")} aria-label="Dismiss error">
            ×
          </button>
        </div>
      )}
      {s.job && (
        <div
          className={`job-banner ${s.job.status}`}
          role="status"
          aria-live="polite"
        >
          <Icon
            name={s.job.status === "completed" ? "check" : "clock"}
            size={16}
          />
          <span>{s.job.stage}</span>
          {s.job.progress !== null && s.job.progress !== undefined && (
            <progress
              max={1}
              value={s.job.progress}
              aria-label="Render progress"
            />
          )}
          {s.job.elapsed && <small>{s.job.elapsed.toFixed(1)}s elapsed</small>}
        </div>
      )}
      <nav className="mobile-tabs" aria-label="Workspace sections">
        {["preview", "assets", "effects", "direction", "storyboard"].map(
          (tab) => (
            <button
              key={tab}
              className={mobileTab === tab ? "active" : ""}
              onClick={() => {
                setMobileTab(tab);
                if (tab === "assets" || tab === "effects") setLeftMode(tab);
              }}
              aria-pressed={mobileTab === tab}
            >
              {tab[0].toUpperCase() + tab.slice(1)}
            </button>
          ),
        )}
      </nav>
      <div className={`workspace mobile-${mobileTab}`}>
        <div className="assets-slot">
          <nav className="side-modes" aria-label="Assets and effects">
            {["assets", "effects"].map((mode) => (
              <button
                key={mode}
                className={leftMode === mode ? "active" : ""}
                aria-pressed={leftMode === mode}
                onClick={() => setLeftMode(mode)}
              >
                {mode === "assets" ? "Assets" : "45 Effects"}
              </button>
            ))}
          </nav>
          {leftMode === "effects" ? (
            <EffectBrowser
              version={version}
              assets={s.project?.assets || []}
              busy={s.busy}
              onDirection={() => setMobileTab("direction")}
              onApply={async (params, start, end) => {
                const ok = await s.applyEffect(params, start, end);
                if (ok) setMobileTab("preview");
                return ok;
              }}
            />
          ) : (
            <Assets
              assets={s.project?.assets || []}
              sourceId={s.sourceId}
              referenceId={s.referenceId}
              onSource={s.setSourceId}
              onReference={s.setReferenceId}
              onUpload={s.upload}
              disabled={s.busy}
            />
          )}
        </div>
        <div className="preview-slot">
          <Preview
            projectId={s.project?.id}
            source={source}
            version={version}
            original={original}
            onOriginal={setOriginal}
            busy={s.busy}
          />
          <div className="version-bar">
            <label htmlFor="version">
              <Icon name="clock" size={15} />
              Version
            </label>
            <select
              id="version"
              value={s.versionId}
              onChange={(e) => {
                s.setVersionId(e.target.value);
                setOriginal(false);
              }}
              disabled={s.busy || !s.project?.versions.length}
            >
              <option value="" disabled>
                No drafts yet
              </option>
              {s.project?.versions.map((v, i) => (
                <option value={v.id} key={v.id}>
                  v{s.project!.versions.length - i} · {v.summary}
                </option>
              ))}
            </select>
            {version?.has_preview &&
              s.project?.current_version_id !== version.id && (
                <button
                  className="text-button"
                  onClick={s.restore}
                  disabled={s.busy}
                >
                  Restore
                </button>
              )}
          </div>
          <Timeline version={version} />
          {version && !version.has_preview && (
            <button
              className="primary wide"
              onClick={() =>
                s.start({
                  action: "render",
                  version_id: version.id,
                  quality: "preview",
                })
              }
              disabled={s.busy}
            >
              Render this storyboard
              <Icon name="arrow" size={17} />
            </button>
          )}
          {version?.has_export && (
            <div className="download-bar">
              <span>
                <Icon name="check" size={17} /> Your 1080p export is ready.
              </span>
              <a
                className="primary"
                href={`${prefix}/versions/${version.id}/export`}
              >
                Download MP4
              </a>
            </div>
          )}
          {version && (
            <a
              className="plan-link"
              href={`${prefix}/versions/${version.id}/plan`}
            >
              Download editing plan ↗
            </a>
          )}
          {!source && (
            <button
              className="mobile-upload-cta primary wide"
              onClick={() => setMobileTab("assets")}
            >
              <Icon name="upload" size={17} /> Add your footage
            </button>
          )}
        </div>
        <div className="direction-slot">
          <Direction
            projectId={s.project?.id}
            version={version}
            job={s.job}
            busy={s.busy}
            canDraft={!!s.sourceId && !!s.health?.meta_configured}
            onDraft={draft}
            onRevise={(instruction) =>
              s.start({
                action: "revise",
                version_id: version?.id,
                instruction,
              })
            }
            subjectId={s.subjectId}
            onSubject={s.setSubjectId}
          />
          {version && (
            <button
              className="text-button new-draft"
              onClick={() => s.setVersionId("")}
              disabled={s.busy}
            >
              Create a new direction
            </button>
          )}
        </div>
        <div className="storyboard-slot">
          <Timeline version={version} />
          {version ? (
            <>
              <ol className="storyboard-beats">
                {version.storyboard.map((beat) => (
                  <li key={beat.operation_id}>
                    <span className="eyebrow">
                      {beat.start.toFixed(1)}–{beat.end.toFixed(1)}s
                    </span>
                    <h2>{beat.text || beat.type.replaceAll("_", " ")}</h2>
                    <p>{beat.reason}</p>
                  </li>
                ))}
              </ol>
              <a
                className="plan-link"
                href={`${prefix}/versions/${version.id}/plan`}
              >
                Download editing plan ↗
              </a>
            </>
          ) : (
            <div className="storyboard-hint">
              <h2>Every edit starts with a plan.</h2>
              <p>
                Your beats and creative decisions will appear here after you
                create a draft.
              </p>
            </div>
          )}
        </div>
      </div>
      <footer className="app-footer">
        <span>Made with intention. Powered by Meta.</span>
        <span>
          Local API allowance reserved: ${s.reserved.toFixed(2)} / $
          {s.limit.toFixed(0)}{" "}
          <span title="Conservative request allowances, not confirmed provider billing">
            ⓘ
          </span>
        </span>
      </footer>
    </main>
  );
}
