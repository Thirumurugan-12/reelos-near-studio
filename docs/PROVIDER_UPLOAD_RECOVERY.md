# Provider-upload recovery after API-key changes

On 31 October 2026, a small Muse inference worked with the replacement key, but the
full-source planning request failed with HTTP 404. A read-only diagnostic confirmed:
- `GET /v1/models`: HTTP 200, configured Muse model listed.
- `GET /v1/files/<cached-source-id>`: HTTP 404, `file_not_found`.

The cached upload was not accessible with the current key. This can happen after a
key/account change or when a provider file expires; these observations do not identify
which lifecycle event removed access. Repeating the same inference with that file ID
would not repair it.

`Editor.provider_file` now checks cached file visibility through Meta's documented
file-metadata endpoint before reuse. A definite 404 causes a fresh proxy upload; a
visible file is reused. Authentication/access errors propagate rather than triggering
an upload. A failed replacement upload leaves the previous stored record intact.
Source-specific SAM masks and speech transcripts remain reusable: they are derived
source data rather than key-scoped provider file IDs.

Meta response errors now preserve a bounded, credential-redacted `code`, `type` and
`message` in the returned error and private `responses/<call>.error.json` diagnostics.
No request headers, prompts or API key are copied. Inference is never automatically
retried, and failed/unknown calls retain conservative reservations.

Validation: 88 backend tests pass; Ruff passes. Regressions cover inaccessible/visible
cached uploads, failed replacement preserving state, metadata 404 versus 403, no
inference reservation for metadata checks, and redaction of a key echoed by an error.
Official references: [error handling](https://dev.meta.ai/docs/error-handling),
[authentication](https://dev.meta.ai/docs/authentication).

The user explicitly approved raising the local reservation guardrail from $50 to $75.
Only `REELOS_API_BUDGET_USD` was updated locally; credentials remain untracked. The
backend was deployed only after confirming there were no active jobs, and its health
endpoint reports the $75 cap. This does not alter or represent Meta's credit balance.

A fresh source-only full-video planning job was dispatched after deployment:
`bdbac06cb9f144bc814de4a2f1b59fd7`. It supplies no reference video and no parent plan.
Private job/usage evidence is stored in `data/no-reference-review/`.

## Successful fresh Muse planning

After upload refresh, job `bdbac06cb9f144bc814de4a2f1b59fd7` completed successfully.
Muse created source-only version `c25a3c2c5ac9475d9e03aa32779db475` (v21), with no
parent and no reference input. Exactly one new Muse call completed: 66,310 input
and 2,913 output tokens, 23.57s provider latency, $0.09526775 estimated from reported
usage. SAM and source ASR were reused from their source-specific caches.

Muse chose blue accents, editorial animated headlines, two tracked callouts, five
supporting B-roll cards and a continuous subject focus/contour. The raw model plan
and source-only observations are preserved privately and in the original version.

Editorial review changed exactly three copy fields in child
`7d7cc51f54a3460fb7cc8b59597490fc` (v22):
- Childhood card body: clarify that the childhood wish was to wear glasses.
- Stage card title: describe blurred faces rather than absence of sight.
- Eye-check headline: use a neutral conversation heading instead of an outcome promise.

All effect choices, palette, framing, source interval and timing remain Muse's.
The review diff is retained in `reviewed-muse-copy-changes.json`. The child inherits
actual SAM tracking and original source-only observations from the model version.
It was rendered in full at preview and export resolutions without further
paid model requests.

## Completed reviewed Muse export

Current **v22**, `7d7cc51f54a3460fb7cc8b59597490fc`, has both playable preview and
1080p export. Preview worker time was 152.33s; export was 497.43s. The export is
167.900s, 1080×1920, 5,037 H.264 frames plus AAC, 149,985,556 bytes. Both files
decode fully without errors. The exported 13s card was visually inspected, as were
nine preview positions covering all five cards, chapter headings and closing CTA.

Demuxed audio SHA-256 is unchanged from earlier full-recording versions:
`b1e124e9c45a4cdab6b0160a9bf8c2f5757de58c6d688f175d919d1cd2847ff6`.
The preview loaded and played in the native browser. In-app v22 playback was verified
with no media error; the mobile document and viewport are both 390×844. The current
workspace was left with No reference selected for the next draft.

The live API confirms raw source-only Muse provenance, exactly the three documented
copy edits, unchanged model/reviewed plans, current v22 and preserved v18/v19/v20
exports. Accurate version labels and provenance were attached after all jobs finished;
no plan or artifact was changed by that metadata update. The ledger reports $51
reserved of $75, $1.30135175 estimated known usage, and five unpriced calls. These
remain local accounting values rather than confirmed Meta billing.

Private output: `data/no-reference-review/muse-source-only-export.mp4`. Review frames,
job/call evidence and `muse-workspace.png` are retained alongside it and ignored by Git.
