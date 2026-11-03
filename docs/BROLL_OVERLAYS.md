# Supporting assets over live footage

`GraphicStyle.presentation` now supports `broll` and `fullscreen`. Omitted values
retain the previous full-screen behavior, preserving older plan snapshots and renders.
The planner and minimal revision schema expose the supported layout choice.

B-roll presentation keeps the actual talking-head edit running and composites a compact
animated card across the lower 29% of the portrait frame. It contains the central
illustration from the existing approved Remotion asset, a bold title and concise copy.
The card enters over 420ms with cubic easing and fades out over its final 220ms.
It occupies 88% of the frame width and leaves the upper 65% of the frame untouched.
The speaker's voice continues through every supporting asset beat.

This is a B-roll style treatment of the existing generated illustrations, not newly
sourced live-action footage. Source photos already embedded in the uploaded recording
remain part of that source. No additional external footage or model generation is used.

The layout field is excluded from Remotion input props and cache keys: changing the
presentation reuses the previously rendered illustration sequence. The shared engine
composites the same layout for web, CLI, preview and export. The underlying full-screen
Remotion templates remain available for explicit full-screen cutaways.

Verification includes preservation of source pixels above/outside the card, transparent
entry, unchanged legacy serialization and full-screen behavior, exact targeted revision
preservation, and cache reuse without a new Remotion render. All 83 backend tests and
Ruff pass. Source-footage layout review is in `data/broll-review/layout.png`.

The actual full recording is rendered as a child of animated-text v18
`03b4db6a2df44257939884b0fda03e68`. All six illustration beats use B-roll presentation;
the five animated headlines, four callouts, source interval, framing and spotlight
remain unchanged. v18 remains available for comparison.

## Disk-full recovery during verification

The first preview job `a6b120c467d9469ca2a39f4a2cfbe2ca` failed at 85% when
Docker Desktop reported `no space left on device` while writing its VM log. The
local frontend subsequently refused connections. No incomplete preview was promoted.
The project, parent v18 and new child `901023f71be540c9a6087f60d531a233` persisted.

Cleared the re-downloadable npm content cache (about 13GB), leaving about 20GB free,
then stopped/restarted the failed Docker runtime with its official Desktop CLI.
No user footage, project records, Docker volumes, installed dependencies or prior
exports were deleted. The existing child was rendered again successfully; no additional
model request or duplicate edit version was created. Evidence is preserved in
`data/broll-review/result.json` and `recovered-state.json`; resumed jobs are tracked
separately in `recovery.json`.

## Encoded preview checks

The resumed preview completed in 145.25s. It is 167.900s long with 5,037 H.264
frames at 360×640 plus AAC, and it decodes fully without errors. Frames at 13s,
37s, 69s, 96s, 126s and 149s were inspected together: all six card layouts keep
the speaker's face visible above the supporting asset. Evidence:
`data/broll-review/all-six-broll-beats.png`.

The preview's demuxed AAC SHA-256 remains
`b1e124e9c45a4cdab6b0160a9bf8c2f5757de58c6d688f175d919d1cd2847ff6`, identical
to v18 and the earlier full recording exports. Native browser playback shows the
new glasses card at 13s (`browser-playback.png`).

## Completed export

Version **v19**, `901023f71be540c9a6087f60d531a233`, is now current in ReelOS.
Its resumed 1080p export completed in 532.59s. The file is 143,932,311 bytes,
167.900s, 1080×1920, 5,037 H.264 frames plus AAC. It decodes in full without
errors, and its demuxed AAC hash matches v18 exactly. The exported glasses card
was visually inspected (`data/broll-review/export-card.png`). Native browser
preview playback reached `ended=true` at 167.9s with no media error.

The mobile workspace plays v19 and exposes its new export link; document and
viewport dimensions are both 390×844 with no page scrolling. Evidence is saved
in `data/broll-review/mobile-workspace.png`. The live API confirms that v18
still has its preview/export, and the only six plan differences are the asset
presentation fields. No new paid model request was made; the reservation remains $46.

Full private outputs:
- `data/broll-review/full-broll-preview.mp4`
- `data/broll-review/full-broll-export.mp4`

## Renderer note (3 November 2026)

The illustration sequences behind both presentations now render through HyperFrames by default
(`graphics/hyperframes/`), with the same 1080×1920, 30 fps PNG-plus-manifest contract, the same frame
counts and the same illustration band (y 28–65%) that the b-roll crop uses. Cache keys include the
renderer, so existing Remotion sequences and already exported versions are untouched.
`REELOS_GRAPHICS_RENDERER=remotion` restores the Remotion templates. See [dependencies](DEPENDENCIES.md).
