import { useState } from "react";
import { type Job, type Version } from "../lib/api";
import { Icon } from "./icons";

export function Direction({
  version,
  job,
  busy,
  canDraft,
  onDraft,
  onRevise,
  subjectId,
  onSubject,
  projectId,
}: {
  version?: Version;
  job: Job | null;
  busy: boolean;
  canDraft: boolean;
  onDraft: (
    instruction: string,
    review: boolean,
    prompt: string,
    outputMode: "full" | "reel",
  ) => void;
  onRevise: (instruction: string) => void;
  subjectId: string;
  onSubject: (id: string) => void;
  projectId?: string;
}) {
  const [instruction, setInstruction] = useState(
    "A clear, confident explainer. Give the opening a bold headline, keep the focus on me, and add a subtle tracked label.",
  );
  const [revision, setRevision] = useState("");
  const [review, setReview] = useState(false);
  const [subject, setSubject] = useState("person");
  const [outputMode, setOutputMode] = useState<"full" | "reel">("full");
  const needsSubject =
    job?.status === "needs_subject" && job.request.subject_prompt === subject;
  return (
    <section className="direction panel" aria-label="Creative direction">
      <div className="panel-heading">
        <h2>Creative direction</h2>
        <span className="spark-mark">
          <Icon name="sparkle" size={16} />
        </span>
      </div>
      <p className="muted small">A little intention goes a long way.</p>
      {!version ? (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onDraft(instruction, review, subject, outputMode);
          }}
        >
          <label className="field-label" htmlFor="direction">
            What do you have in mind?
          </label>
          <textarea
            id="direction"
            value={instruction}
            maxLength={2000}
            onChange={(e) => setInstruction(e.target.value)}
            rows={5}
            disabled={busy}
          />
          <label className="field-label" htmlFor="output-mode">
            Edit length
          </label>
          <select
            id="output-mode"
            value={outputMode}
            onChange={(e) => setOutputMode(e.target.value as "full" | "reel")}
            disabled={busy}
          >
            <option value="full">
              Full video · preserve the complete recording
            </option>
            <option value="reel">Short reel · 15–30 second excerpt</option>
          </select>
          <label className="field-label" htmlFor="subject">
            Subject to track
          </label>
          <input
            id="subject"
            value={subject}
            maxLength={120}
            onChange={(e) => {
              setSubject(e.target.value);
              onSubject("");
            }}
            disabled={busy}
          />
          {needsSubject && (
            <fieldset className="subject-choice">
              <legend>Who should we track?</legend>
              <p className="small muted">
                Choose the highlighted person to use in your edit.
              </p>
              <div className="subject-grid">
                {job.result?.subjects.map((id) => (
                  <label key={id} className="subject-card">
                    <input
                      type="radio"
                      name="tracked-subject"
                      value={id}
                      checked={subjectId === id}
                      onChange={() => onSubject(id)}
                      disabled={busy}
                    />
                    {/* Local thumbnails already have the correct display size. */}
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={`/api/projects/${projectId}/jobs/${job.id}/subjects/${id}/thumbnail`}
                      alt={`Highlighted subject ${id}`}
                      width={192}
                      height={192}
                    />
                    <span>Subject {id}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          )}
          <label className="checkbox">
            <input
              type="checkbox"
              checked={review}
              onChange={(e) => setReview(e.target.checked)}
              disabled={busy}
            />{" "}
            Review storyboard before rendering
          </label>
          <button
            className="primary wide"
            disabled={
              busy ||
              !canDraft ||
              !subject.trim() ||
              (needsSubject && !subjectId)
            }
          >
            <Icon name="sparkle" size={17} />
            {busy ? "Creating your edit…" : "Create draft"}
            <Icon name="arrow" size={17} />
          </button>
          <p className="privacy-note">
            Creating a draft sends your proxy footage to Meta for analysis and
            subject tracking.
          </p>
        </form>
      ) : (
        <>
          <div className="edit-summary">
            <span className="eyebrow">EDITOR’S NOTE</span>
            <p>{version.summary}</p>
          </div>
          <div className="decisions">
            {version.storyboard.map((beat) => (
              <div className="decision" key={beat.operation_id}>
                <span>{beat.start.toFixed(1)}s</span>
                <p>
                  {beat.reason || beat.text || beat.type.replaceAll("_", " ")}
                </p>
              </div>
            ))}
          </div>
          <form
            className="revision-form"
            onSubmit={(e) => {
              e.preventDefault();
              if (revision.trim()) onRevise(revision);
            }}
          >
            <label className="field-label" htmlFor="revision">
              Make it yours
            </label>
            <textarea
              id="revision"
              value={revision}
              onChange={(e) => setRevision(e.target.value)}
              placeholder="Lower the headline and soften the spotlight…"
              rows={3}
              maxLength={2000}
              disabled={busy}
            />
            <div className="suggestions">
              {[
                "Lower the headline",
                "Soften the spotlight",
                "Make the opening faster",
              ].map((text) => (
                <button
                  type="button"
                  key={text}
                  onClick={() => setRevision(text)}
                  disabled={busy}
                >
                  {text}
                </button>
              ))}
            </div>
            <button
              className="primary wide"
              disabled={busy || !revision.trim()}
            >
              Apply changes
              <Icon name="arrow" size={17} />
            </button>
          </form>
          {version.observations.length > 0 && (
            <details>
              <summary>Footage & reference observations</summary>
              {version.observations.map((o, i) => (
                <p className="small" key={i}>
                  <strong>{o.origin}:</strong> {o.text}
                </p>
              ))}
            </details>
          )}
        </>
      )}
    </section>
  );
}
