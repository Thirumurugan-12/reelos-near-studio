"use client";

import { useEffect, useRef, useState } from "react";
import { useStudio } from "../lib/use-studio";
import { time } from "../lib/api";
import { Assets } from "../components/assets";
import { Direction } from "../components/direction";
import { Preview } from "../components/preview";
import { Timeline, effectLabel } from "../components/timeline";
import { EffectBrowser } from "../components/effect-browser";
import { Icon } from "../components/icons";
import { VersionHistory } from "../components/version-history";
import { ReelPanel, isReel, reelClips } from "../components/reel-panel";

type Tool = "edit" | "effects" | "media" | "moment";
const toolItems = [
  { id: "edit", label: "Edit", icon: "layers" },
  { id: "effects", label: "Looks", icon: "sparkle" },
  { id: "media", label: "Media", icon: "film" },
] as const;
const quickTreatments = [
  { fx: "backdrop-word", label: "Bold type" },
  { fx: "orbit", label: "Orbit cards" },
  { fx: "spotlight", label: "Spotlight" },
];

export default function Studio() {
  const s = useStudio();
  const [tool, setTool] = useState<Tool>("edit");
  const [sheetOpen, setSheetOpen] = useState(false);
  const [initialFx, setInitialFx] = useState<string>();
  const [selectedId, setSelectedId] = useState<string>();
  const [focusedId, setFocusedId] = useState<string>();
  const [original, setOriginal] = useState(false);
  const [dismissedJobError, setDismissedJobError] = useState<string>();
  const [playhead, setPlayhead] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const sheetCloseRef = useRef<HTMLButtonElement>(null);
  const historyRef = useRef<HTMLDialogElement>(null);
  const toolRef = useRef<HTMLElement | null>(null);
  const version = s.project?.versions.find((v) => v.id === s.versionId);
  const selected = version?.plan.effects.find((e) => e.id === selectedId);
  const focused = version?.plan.effects.find((e) => e.id === focusedId);
  const source = s.project?.assets.find(
    (a) => a.id === (version?.plan.asset_id || s.sourceId),
  );
  const clips = reelClips(s.project?.assets || []);
  const onReel = isReel(version);
  const reelMode = clips.length >= 2 && (!s.sourceId || onReel || !version);
  const previewSource = onReel
    ? undefined
    : source || (!version && !s.sourceId ? clips[0] : undefined);
  const mode = tool === "moment" && !selected ? "edit" : tool;
  const prefix = s.project ? `/api/projects/${s.project.id}` : "";
  const versionNumber = version
    ? s.project!.versions.length - s.project!.versions.indexOf(version)
    : 0;
  function openTool(next: Tool, trigger?: HTMLButtonElement) {
    setTool(next);
    setSheetOpen(true);
    setInitialFx(undefined);
    if (next === "edit") setFocusedId(undefined);
    if (trigger) toolRef.current = trigger;
  }
  function closeSheet() {
    setSheetOpen(false);
    toolRef.current?.focus();
  }
  function seekTo(seconds: number) {
    const video = videoRef.current;
    if (!video) return;
    const target = seconds + (original && version ? version.plan.source_in : 0);
    const apply = () => {
      video.currentTime = Math.min(
        Math.max(0, target),
        Number.isFinite(video.duration) ? video.duration : target,
      );
    };
    if (video.readyState >= 1) apply();
    else video.addEventListener("loadedmetadata", apply, { once: true });
    setPlayhead(seconds);
  }
  useEffect(() => {
    if (s.job?.status === "needs_subject") {
      setTool("edit");
      setSheetOpen(true);
    }
  }, [s.job?.status]);
  useEffect(() => {
    if (sheetOpen && window.matchMedia("(max-width: 767px)").matches)
      sheetCloseRef.current?.focus();
  }, [sheetOpen, mode]);
  const visibleError =
    s.error ||
    (s.job?.status === "failed" && s.job.id !== dismissedJobError
      ? s.job.error ||
        "The last edit did not finish. Your saved versions are still available."
      : "");
  const status = s.busy
    ? s.job && ["queued", "running"].includes(s.job.status)
      ? s.job.stage
      : "Preparing your media…"
    : version?.has_preview
      ? "Preview ready"
      : version
        ? "Storyboard ready"
        : source || clips.length
          ? "Ready for your direction"
          : "Add footage to begin";
  return (
    <main className="studio">
      <header className="app-header">
        <a href="/" className="wordmark" aria-label="ReelOS home">
          reel<span>os</span>
        </a>
        <div className="project-picker">
          <label className="sr-only" htmlFor="project">
            Project
          </label>
          <select
            id="project"
            value={s.project?.id || ""}
            disabled={s.busy}
            onChange={(e) => {
              s.select(e.target.value);
              setSelectedId(undefined);
              setFocusedId(undefined);
              setOriginal(false);
            }}
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
            aria-label="New project"
            disabled={s.busy}
            onClick={async () => {
              await s.create();
              openTool("media");
            }}
          >
            <Icon name="plus" size={16} />
          </button>
        </div>
        <div className="header-end">
          <a className="history-button" href={s.project ? `/orders?project=${s.project.id}` : "/orders"}>Paid studio ↗</a>
          <button
            className="history-button"
            aria-label="Version history"
            onClick={() => historyRef.current?.showModal()}
            disabled={!s.project}
          >
            <Icon name="clock" size={16} />
            <span className="history-label">
              {version ? `v${versionNumber} · History` : "History"}
            </span>
          </button>
          {version?.has_export ? (
            <a
              className="primary export-button"
              href={`${prefix}/versions/${version.id}/export`}
              aria-label="Download MP4"
            >
              <span>Download</span>
              <Icon name="download" size={14} />
            </a>
          ) : (
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
              <span>Export</span>
              <Icon name="arrow" size={14} />
            </button>
          )}
        </div>
      </header>
      <h1 className="sr-only">{s.project?.name || "ReelOS creative studio"}</h1>
      {visibleError && (
        <div className="error-banner" role="alert">
          <span>{visibleError}</span>
          <button
            aria-label="Dismiss error"
            onClick={() => {
              s.setError("");
              setDismissedJobError(s.job?.id);
            }}
          >
            ×
          </button>
        </div>
      )}
      {s.busy && (
        <div className="job-banner" role="status" aria-live="polite">
          <span className="activity-dot" />
          <span>{status}</span>
          {s.job?.progress != null && (
            <progress
              max={1}
              value={s.job.progress}
              aria-label="Render progress"
            />
          )}
        </div>
      )}
      <div className="workspace">
        <nav className="tool-rail" aria-label="Editor tools">
          {toolItems.map((item) => (
            <button
              key={item.id}
              className={mode === item.id ? "active" : ""}
              aria-pressed={mode === item.id}
              onClick={(e) => openTool(item.id, e.currentTarget)}
            >
              <Icon name={item.icon} size={20} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="canvas-main">
          <Preview
            projectId={s.project?.id}
            source={previewSource}
            version={version}
            original={original}
            onOriginal={setOriginal}
            busy={s.busy}
            videoRef={videoRef}
            onTimeChange={(t) =>
              setPlayhead(
                t - (original && version ? version.plan.source_in : 0),
              )
            }
            onAddFootage={() => openTool("media")}
          />
          <Timeline
            version={version}
            playhead={playhead}
            selectedId={selectedId}
            onSeek={seekTo}
            onSelect={(effect, trigger) => {
              toolRef.current = trigger;
              setSelectedId(effect.id);
              setTool("moment");
              setSheetOpen(true);
            }}
          />
          {version && !version.has_preview && (
            <button
              className="storyboard-render primary"
              disabled={s.busy}
              onClick={() =>
                s.start({
                  action: "render",
                  version_id: version.id,
                  quality: "preview",
                })
              }
            >
              Render storyboard <Icon name="arrow" size={14} />
            </button>
          )}
        </div>
        <aside
          className={`inspector ${sheetOpen ? "sheet-open" : ""}`}
          aria-label="Editor controls"
          onKeyDown={(e) => {
            if (e.key === "Escape") closeSheet();
          }}
        >
          <div className="sheet-grip" />
          <div className="inspector-heading">
            <div>
              <h2>
                {mode === "media"
                  ? "Your media."
                  : mode === "effects"
                    ? "Find your look."
                    : mode === "moment"
                      ? "This moment."
                      : "Make it yours."}
              </h2>
              <p>
                {mode === "media"
                  ? "Footage, references and supporting cards."
                  : mode === "effects"
                    ? "45 treatments. One story: yours."
                    : mode === "moment"
                      ? "Inspect it. Change only what you need."
                      : "A few good choices. Your own story."}
              </p>
            </div>
            <button
              ref={sheetCloseRef}
              className="sheet-close icon-button"
              aria-label="Close controls"
              onClick={closeSheet}
            >
              ×
            </button>
          </div>
          <div className="inspector-content">
            <div hidden={mode !== "edit"}>
              {reelMode && (
                <ReelPanel
                  key={`${s.project?.id}-reel-${version?.id || "new"}`}
                  clips={clips}
                  busy={s.busy}
                  canPlan={!!s.health?.meta_configured}
                  version={onReel ? version : undefined}
                  onMake={(ids, title, direction, style, showTimes) => {
                    s.makeReel(ids, title, direction, style, showTimes);
                    setSheetOpen(false);
                  }}
                  projectId={s.project?.id}
                  onCarousel={() => {
                    s.makeCarousel();
                    setSheetOpen(false);
                  }}
                  onRestyle={(style, showTimes) => {
                    s.restyle(style, showTimes);
                    setSheetOpen(false);
                  }}
                  onAddClips={() => openTool("media")}
                />
              )}
              {version && !onReel && (
                <section
                  className="quick-treatments"
                  aria-label="Quick treatments"
                >
                  <div className="section-heading">
                    <h3>Start with a treatment</h3>
                    <button
                      className="text-button"
                      onClick={() => openTool("effects")}
                    >
                      Browse all →
                    </button>
                  </div>
                  <div className="treatment-grid">
                    {quickTreatments.map((p) => (
                      <button
                        key={p.fx}
                        onClick={() => {
                          setInitialFx(p.fx);
                          setTool("effects");
                          setSheetOpen(true);
                        }}
                      >
                        <img src={`/api/effects/${p.fx}/poster`} alt="" />
                        <span>{p.label}</span>
                      </button>
                    ))}
                  </div>
                </section>
              )}
              {!source && !clips.length && (
                <div className="setup-hint">
                  <span className="eyebrow">
                    01 FOOTAGE → 02 DIRECTION → 03 EDIT
                  </span>
                  <p>
                    Add a recording, or several clips for a reel, in Media. Then
                    tell ReelOS what you want to make.
                  </p>
                  <button
                    className="text-button"
                    onClick={() => openTool("media")}
                  >
                    Add footage →
                  </button>
                </div>
              )}
              {focused && (
                <div className="focus-note">
                  Revising {effectLabel(focused)} · {time(focused.start)}
                  <button
                    className="text-button"
                    onClick={() => setFocusedId(undefined)}
                  >
                    Clear
                  </button>
                </div>
              )}
              {version &&
                !onReel &&
                version.render_profile?.broll_art !== "muse-image" &&
                version.plan.effects.some(
                  (e) => e.type === "graphic_insert",
                ) && (
                  <section className="paint-broll" aria-label="Paint B-roll">
                    <div className="section-heading">
                      <h3>Paint the B-roll</h3>
                      <span className="optional">Muse Image</span>
                    </div>
                    <p className="muted small">
                      Muse Image illustrates each B-roll card from its own text.
                      Same plan, new version.
                    </p>
                    <button
                      className="secondary wide"
                      disabled={s.busy}
                      onClick={() => {
                        s.paintBroll();
                        setSheetOpen(false);
                      }}
                    >
                      Paint B-roll with Muse Image{" "}
                      <Icon name="sparkle" size={14} />
                    </button>
                  </section>
                )}
              {version && !onReel && (
                <fieldset className="framing-controls" disabled={s.busy}>
                  <legend>Framing</legend>
                  <p>
                    Make space above the speaker. Text and timing stay the same.
                  </p>
                  <div className="segmented">
                    {[
                      { label: "Room for titles", scale: 0.82, offset: 0.16 },
                      { label: "Original framing", scale: 1, offset: 0 },
                    ].map((choice) => {
                      const active =
                        (version.plan.framing?.scale ?? 1) === choice.scale &&
                        (version.plan.framing?.offset_y ?? 0) === choice.offset;
                      return (
                        <button
                          key={choice.label}
                          type="button"
                          aria-pressed={active}
                          disabled={active}
                          onClick={() => {
                            s.reframe(choice.scale, choice.offset);
                            setSheetOpen(false);
                          }}
                        >
                          {choice.label}
                        </button>
                      );
                    })}
                  </div>
                </fieldset>
              )}
              {!reelMode && (
                <Direction
                  key={`${s.project?.id}-${version?.id || "draft"}`}
                  projectId={s.project?.id}
                  version={version}
                  job={s.job}
                  busy={s.busy}
                  canDraft={!!s.sourceId && !!s.health?.meta_configured}
                  onDraft={(instruction, review, subject, outputMode) => {
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
                    setSheetOpen(false);
                  }}
                  onRevise={(instruction) => {
                    s.start({
                      action: "revise",
                      version_id: version?.id,
                      instruction: focused
                        ? `Update only effect ${focused.id} (${effectLabel(focused)}, ${focused.start}–${focused.end}s). ${instruction}`
                        : instruction,
                    });
                    setSheetOpen(false);
                  }}
                  focusedLabel={focused ? effectLabel(focused) : undefined}
                  subjectId={s.subjectId}
                  onSubject={s.setSubjectId}
                />
              )}
              {version && !onReel && (
                <button
                  className="text-button new-draft"
                  disabled={s.busy}
                  onClick={() => {
                    s.setVersionId("");
                    setFocusedId(undefined);
                  }}
                >
                  Create a new direction →
                </button>
              )}
            </div>
            {mode === "effects" && (
              <EffectBrowser
                key={initialFx || "all"}
                initialFx={initialFx}
                initialTime={playhead}
                version={version}
                assets={s.project?.assets || []}
                busy={s.busy}
                onDirection={() => openTool("edit")}
                onApply={async (params, start, end) => {
                  const ok = await s.applyEffect(params, start, end);
                  if (ok) setSheetOpen(false);
                  return ok;
                }}
              />
            )}
            {mode === "media" && (
              <>
                <Assets
                  assets={s.project?.assets || []}
                  sourceId={s.sourceId}
                  referenceId={s.referenceId}
                  onSource={s.setSourceId}
                  onReference={s.setReferenceId}
                  onUpload={s.upload}
                  disabled={s.busy}
                />
              </>
            )}
            {mode === "moment" && selected && (
              <section className="moment-detail">
                <span className="eyebrow">
                  {time(selected.start)}—{time(selected.end)}
                </span>
                <h3>{effectLabel(selected)}</h3>
                {selected.params.text && (
                  <p className="moment-copy">
                    {selected.params.text.replaceAll("|", " / ")}
                  </p>
                )}
                <p className="muted">
                  {selected.reason ||
                    "A visual treatment on your original recording."}
                </p>
                {!onReel && (
                  <button
                    className="primary wide"
                    disabled={s.busy}
                    onClick={() => {
                      setFocusedId(selected.id);
                      setTool("edit");
                    }}
                  >
                    Revise this moment <Icon name="arrow" size={14} />
                  </button>
                )}
                <button
                  className="text-button"
                  onClick={() => seekTo(selected.start)}
                >
                  Go to this moment →
                </button>
                <p className="privacy-note">
                  Revisions create a new version. The original edit stays
                  available.
                </p>
              </section>
            )}
          </div>
          {mode === "media" &&
            (s.sourceId || clips.length >= 2) &&
            !version && (
              <div className="inspector-footer">
                <button
                  className="primary wide"
                  disabled={s.busy}
                  onClick={() => openTool("edit")}
                >
                  Continue to direction <Icon name="arrow" size={14} />
                </button>
              </div>
            )}
        </aside>
      </div>
      <footer className="app-footer">
        <span className="studio-state">
          <span className={`state-dot ${s.busy ? "working" : ""}`} />
          {status}
        </span>
        <details className="usage-details">
          <summary>Usage & connection</summary>
          <div>
            <strong>
              {s.health?.meta_configured ? "Meta connected" : "Meta key needed"}
            </strong>
            <p>
              Local allowance reserved: ${s.reserved.toFixed(2)} / $
              {s.limit.toFixed(0)}
            </p>
            <p className="muted">
              Conservative request allowances, not confirmed Meta billing.
            </p>
          </div>
        </details>
      </footer>
      <VersionHistory
        project={s.project}
        version={version}
        busy={s.busy}
        dialogRef={historyRef}
        onRestore={s.restore}
        onSelect={(id) => {
          s.setVersionId(id);
          setOriginal(false);
          setSelectedId(undefined);
          setFocusedId(undefined);
        }}
      />
    </main>
  );
}
