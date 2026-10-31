---
name: reelos-effects
description: Create and revise portrait video edits with the local ReelOS service using Meta Muse planning, SAM subject masks, and a validated effects timeline.
---

# ReelOS effects

Use the running ReelOS backend and its CLI from this repository. The web app and CLI share the same service and artifacts. Read the root README for startup; the CLI prefix from the repository root is `uv --directory backend run reelos`.

Check `health` and `usage` first. Provider keys stay in the server environment. The local ledger reports reserved allowances, not confirmed Meta billing. Input media is uploaded to Meta only as part of an authorized draft request.

Supported inputs: one source up to five minutes and an optional reference up to 60 seconds, each up to 200 MB. Full-video mode preserves the entire source; select it with `draft --full-length` (the web UI defaults to full video). Short-reel mode remains available for outputs up to 30 seconds. Both outputs are portrait. The original effect families are behind-subject text, subject spotlight (including monochrome/black background and a glowing contour), tracked label, and Remotion graphic inserts. Four approved insert templates are glasses, classroom, document_stack, and browser_demo. Use inserts only when requested and make their text relevant to the actual source speech; Muse Voice's approximate transcript is for topic understanding, never exact-word alignment. Exact word-level caption alignment remains unsupported; the catalog below adds designed transitions.

Typical commands:

```text
reelos create "My reel"
reelos upload PROJECT_ID /absolute/path/clip.mp4
reelos draft PROJECT_ID ASSET_ID "Edit the complete recording with chapter headings and a subtle spotlight" --full-length --storyboard-only
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

## Complete effects catalog

ReelOS also implements all **45 recipes plus 3 named looks** from Vibha Ramprakash's MIT-licensed [claude-video-effects](https://github.com/Vibha-Ramprakash/claude-video-effects), with original attribution retained. These are real renderers connected to SAM masks, Muse, the web Effects picker and the CLI. Discover current IDs, allowed options and preview URLs with `reelos effects` or `GET /api/effects`. Full inventory and verification: `docs/EFFECT_CATALOG.md`.

Use `catalog_effect` with validated `params: {fx, text, options, media_ids}`. The extra looks are `glitter-spotlight`, `editorial-cover` and `glass-bento`; they canonicalize to spotlight/sparkle, cover-star/editorial and liquid-glass-graph/bento. The existing four families remain supported. Output has at most 48 placements and three concurrent catalog effects. Overlapping catalog effects must use the same tracked subject. Prefer short intentional windows, readable copy and a clear face; a catalog is not a reason to put every recipe in one creative edit.

```text
reelos effects
reelos upload PROJECT_ID /absolute/path/illustration.png --role supporting
reelos apply PROJECT_ID VERSION_ID orbit --start 2 --end 5 --media SUPPORTING_ASSET_ID
reelos apply PROJECT_ID VERSION_ID spotlight --start 7 --end 10 --text "YOUR STORY"
reelos apply PROJECT_ID VERSION_ID glass-bento --start 12 --end 16 --options-file /absolute/path/metrics.json
```

`apply` creates an immutable child and queues a preview. Use `job --wait` on the returned job ID. Supporting PNG/JPEG/WebP images and videos stay project-scoped; upload them with role `supporting` and pass IDs, never filesystem paths in options. Without supporting assets, card-based recipes use stills sampled from the source. These are not automatically discovered or generated moving B-roll. A style reference is never silently reused as content.

Graphs require explicit numeric values; bento needs donut, kpi and bars. Supply creator-approved data, never invent social proof. Gallery previews and the catalog demonstration use labelled illustrative copy/data. Muse receives recipe metadata and supporting asset names, not an analysis of each supporting image's contents. Local YuNet face anchoring is constrained to the SAM-selected subject, with a mask-head fallback when no face is found.

These recipes provide designed animated text, cards, graphs, transitions and treatments; they do not provide exact word-aligned captions or arbitrary generative video. Pause Point freezes the picture while speech continues. Inspect both mid-effect and transition frames and confirm full-duration export and audio before delivery.
