# Source-only editing and pipeline

A style reference is optional. The source file, subject selection, chosen output mode,
creative direction and supported effect schema are sufficient inputs to `draft`.
The no-reference branch sends Muse only the source proxy and its speech transcript,
plus the editing rules/schema. It does not load a previous version's plan.

## Actual pipeline

1. Upload/inspect media, preserve the original and make a small analysis proxy.
2. Run SAM on the source to track the selected person; cache the source-specific masks.
3. Transcribe original audio with Muse Voice ASR; cache the approximate transcript.
4. Muse examines the source proxy and transcript and proposes observations and a JSON
   edit plan: source interval, framing, effect times, copy, palette and supported styles.
   A reference video is an additional optional style input at this step.
5. Validate that plan against the supported effects, selected source/subject, timing,
   output duration and resource limits. Full mode must retain the complete source.
6. Render approved Remotion illustrations. Composite foreground-aware titles,
   spotlights, labels and B-roll with the shared Pillow renderer, then encode/mux with
   FFmpeg. Original speech timing is preserved. Preview is 360p; export is 1080p.
7. Store the version and its artifacts. Conversational changes patch selected fields
   into a new version; comparison/restore retains earlier results.

Without a reference, Muse works within the same available styles and templates;
it selects a suitable treatment from content and user instructions instead of
matching a reference palette/layout. This is structured planning followed by a
bounded renderer, not arbitrary generated editing code. ASR/topic timing is
approximate and is not used as word-aligned captions.

## What happened in this demonstration

A fresh source-only Muse request was actually attempted with `reference_id: null`,
full mode and no parent edit. Job `16b03e9e43214c9785b4e584cc5206f7` failed when
Meta returned **HTTP 402**. It was not retried. The paid ledger retains one conservative
reservation for that failed/unknown call; the local reservation total is now $47.
No successful fresh Muse plan is claimed for this run. Billing/credits need checking
before the fully automatic planning step can be demonstrated again.

To still provide a watchable source-only example, the assistant authored a new plan
from the original footage and cached source transcript, retaining the original SAM
track. This is an explicitly labelled manual planning fallback for this demonstration,
not an automatic product fallback or an output attributed to Muse.

Independent version: `5c22734bfe2241b5a14b4c0dc38b11e8` (v20).
Parent: **none**. Reference: **none**. No earlier plan was copied.
The version's summary/provenance explicitly identify manual planning and HTTP 402.
The underlying source and SAM masks are legitimately reusable across looks because
they represent source content, not reference styling.

The source-only treatment uses natural footage colour, teal/cream editorial titles,
six story headings, three tracked contextual callouts, four compact B-roll cards and
two brief subtle emphasis intervals. No continuous contour or monochrome treatment
is used. Themes come from the speaker's childhood glasses story, school/stage memories,
eye-check discussion and closing ring-light/glasses explanation. Headings are editorial
labels, not fabricated quotations; topical timings remain approximate.

Preview completed in 83.05s: 167.900s, 5,037 H.264 frames at 360×640 with AAC. Frames
at 3s, 20s, 45s, 65s, 130s and 159s were inspected. Preview audio has unchanged
SHA-256 `b1e124e9c45a4cdab6b0160a9bf8c2f5757de58c6d688f175d919d1cd2847ff6`.

Private evidence is retained under `data/no-reference-review/`: the failed planning
request/job, failed-call ledger evidence, authored plan/provenance, saved version,
render job records, review frames, preview and export. Source transcripts and media
remain ignored rather than committed.

## Completed export and provenance verification

The full 1080p export completed in 361.96s. It contains 5,037 H.264 frames at
1080×1920 plus AAC, lasts 167.900s and is 158,010,175 bytes. The complete file
decodes without errors. Its audio hash is identical to the unchanged preview/earlier
full exports above. The exported 20s B-roll frame was visually inspected. Native
browser preview playback reached `ended=true` at 167.9s with no media error.

The live API confirms a null parent, `reference_id: null` in provenance,
`fresh_muse_plan: false`, source-only observations, both completed artifacts and
retained v18/v19 exports. The workspace shows v20 with its explicit manual-plan
label. “No reference” was selected in Assets for the current editing session; this
selector controls the next draft's input and is not proof of a past model request.
The saved request/provenance provide that evidence. Existing reference assets were
retained; the sample did not use them. On a project reload, explicitly select “No
reference” again because the current UI initializes from existing project assets.

Private outputs:
- `data/no-reference-review/source-only-preview.mp4`
- `data/no-reference-review/source-only-export.mp4`
- `data/no-reference-review/source-only-review.png`
- `data/no-reference-review/no-reference-selection.png`

No production code was changed for this example. At creation, the automatic Muse path was
blocked by the provider's HTTP 402; the
completed manually planned example must not be presented as a successful fresh
Muse planning run.

## Access restored after key update — 31 October 2026

The user updated the API key. A secret-safe comparison showed that the running
Compose backend still held the previous key while the local `.env` held the new one.
With no jobs active, the backend was recreated to load the updated environment.
A single small `muse-spark-1.3` inference then completed with HTTP 200 and output
`OK` (13 input tokens, 137 output tokens). Diagnostic evidence is privately retained
in `data/no-reference-review/new-key-check-2026-10-31.json`; it contains no key.

This confirms fresh inference works with the updated runtime key. The full-source
planning request has not yet been rerun with that key, and v20 remains correctly
labelled as an assistant-authored source-only example.
