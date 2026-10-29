---
name: reelos-effects
description: Create and revise portrait video edits with the local ReelOS service using Meta Muse planning, SAM subject masks, and a validated effects timeline.
---

# ReelOS effects

Use the running ReelOS backend and its CLI from this repository. The web app and CLI share the same service and artifacts. Read the root README for startup; the CLI prefix from the repository root is `uv --directory backend run reelos`.

Check `health` and `usage` first. Provider keys stay in the server environment. The local ledger reports reserved allowances, not confirmed Meta billing. Input media is uploaded to Meta only as part of an authorized draft request.

Supported inputs: one source up to 60 seconds, optional reference up to 30 seconds. Output is up to 30 seconds, portrait. Implemented effect types are behind-subject text, subject spotlight, and tracked label. Word-level captions and elaborate transitions are unsupported.

Typical commands:

```text
reelos create "My reel"
reelos upload PROJECT_ID /absolute/path/clip.mp4
reelos draft PROJECT_ID ASSET_ID "A bold introduction with a subtle spotlight" --storyboard-only
reelos job PROJECT_ID JOB_ID --wait
reelos plan PROJECT_ID VERSION_ID
reelos render PROJECT_ID VERSION_ID --quality preview
reelos revise PROJECT_ID VERSION_ID "Lower the headline and soften the spotlight"
reelos render PROJECT_ID VERSION_ID --quality export
```

Retain returned IDs. `job --wait` waits on the existing job; it does not create a new request. On failure or timeout, inspect the same job before deciding to retry, because a provider request may have completed. Never repeat a paid request automatically after an unknown outcome.

If the job needs subject selection, use its returned tracked subject IDs with `draft --subject-id ID`. Ask the creator when identity is ambiguous. Honor explicit storyboard review instructions before rendering. Revisions create versions rather than overwrite earlier outputs. Preserve the canonical plan's source/output time mapping and never substitute arbitrary generated shell commands.

Preview and export URLs are `/api/projects/PROJECT_ID/versions/VERSION_ID/preview` and `/export` on the application origin. Check that an artifact exists and plays before reporting success. Explain unsupported operations rather than claiming a preset reproduces an arbitrary reference.

Before accepting an edit, inspect representative frames and playback against the source. A barely visible headline or subtle parameter change is not evidence of a polished edit. For close-ups, the framed layout can create title headroom while moving SAM masks with the source. Keep the face clear, make the treatment readable, and report the actual operations and limitations. See the repository's `docs/EDITOR_REFERENCE_INTEGRATION.md` for source attribution and the editing workflow.
