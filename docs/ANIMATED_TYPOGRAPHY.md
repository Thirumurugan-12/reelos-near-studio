# Designed text in the actual ReelOS edit

The shared Pillow/FFmpeg renderer now supports `params.design: "editorial" | "pixel"`
on `behind_subject_text` and `tracked_label`. This changes the actual encoded video,
including both 360p previews and 1080p exports. Remotion graphic cutaways continue to
use their existing illustrated animation.

Editorial uses bundled Geist Black; pixel uses bundled Geist Pixel Square. Upstream
font licences and exact file hashes are in `backend/reelos/fonts/README.md`. No network
or platform font lookup occurs during rendering.

The version-one motion is deterministic at 30fps: each word starts 90ms after the
previous word (stagger capped at 650ms), moves upward over 400ms with cubic ease-out,
then holds. All words settle within 1.05s. The final 220ms fades out. Headlines use an
accent tab on the last line; tracked labels use charcoal pills and accent underlines.
Explicit line breaks are preserved. Automatic two-line layout is used for longer
unbroken headlines. The accent defaults to red and can be explicitly overridden with
`accent_color`; `color` controls the glyph fill. Titles retain real SAM foreground
occlusion, and labels retain tracked anchor motion.

The plan snapshot freezes each effect's design, color, accent, size and position.
Legacy plans omit the new optional fields and keep their previous renderer. Minimal
Muse revisions can change `design` or `accent_color` without rewriting other fields.
The planner receives the supported styles and the instruction that explicit user
styling overrides a reference palette. This is a bounded text treatment, not generated
CSS, arbitrary fonts, word-aligned subtitles, or an unrestricted motion-design system.

## Full user recording

Parent: `673e9071da774bbcb3e00444dbb6d576` (v17).
Designed child: `03b4db6a2df44257939884b0fda03e68` (v18).
Source: `6cf53766582d495ebfeeef1fe25107d4`, full 167.9004s with original speech timing.

All five headline beats and all four labels use the new design. The middle “EVERY / DAY”
beat uses pixel type; the other titles use bold editorial type with off-white glyphs
and red accents. The opening starts at 0.3s so the design is visible immediately.
The existing six Remotion inserts, continuous spotlight, and full recording remain.
Rendering reuses cached SAM/Remotion assets and makes no paid model call.

Validation: 79 backend tests pass, including deterministic reveal/hold/exit, both actual
font faces, rendered accent/glyph pixels, foreground occlusion, preview/export bounds,
legacy plan serialization, and exact targeted style revision preservation. Ruff passes.
Source-frame review: `data/typography-review/entrance.png`.
Full render and playback measurements follow.

Preview verification: 147.52s worker time; 167.900s output, 5,037 H.264 frames at
360×640 plus AAC. The entire preview decodes cleanly. Extracted frames at 1.5s,
76.5s and 157s show the editorial opening, pixel middle beat and styled final callout.
Its demuxed AAC SHA-256 is identical to the previous full preview:
`b1e124e9c45a4cdab6b0160a9bf8c2f5757de58c6d688f175d919d1cd2847ff6`.
This establishes that the typography pass did not alter the encoded preview audio.

Export verification: 587.45s worker time; 167.900s,
5,037 H.264 frames, 1080×1920, AAC, 135,732,477 bytes. The complete export decodes
without errors. The exported audio has the same demuxed SHA-256 as the previous
1080p export and as the preview above. Export frames at 1.5s, 76.5s and 157s were
visually inspected. Native browser playback of the complete preview reached
`ended=true` at 167.9s with no media error. In-app v18 playback shows the new opening
title, and the download points to the new 1080p export. The mobile document and
viewport both measure 390×844 with no page overflow.

Outputs and evidence (private, ignored):
- `data/typography-review/full-animated-preview.mp4`
- `data/typography-review/full-animated-export.mp4`
- `data/typography-review/mobile-workspace.png`
- `data/typography-review/result.json`

Live API verification confirmed that v17 retains both its original preview and export,
its plan contains no new design fields, and v18 inherits its same SAM tracking key.
The existing $46 local reservation total is unchanged; this pass made no paid call.
