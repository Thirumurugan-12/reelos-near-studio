# Every treatment on the supplied video

The recording demo now includes **all 45 catalog recipes plus 3 additional looks**. This includes every one of the first 43 recipes requested, plus Messages, Place in Grid and the three looks. The clips are actual rendered edits of the supplied VID_20261012_002734_182_bsl.mp4, not illustrations of hypothetical effects.

## Deliverables

- Updated recording: `data/reelos-hackathon-demo-all-effects.mp4` — 101.400 seconds / 3,042 frames, 1920×1080 H.264/AAC, 83,346,888 bytes. All 48 treatments play in the labelled four-panel gallery from **20.0 to 58.4 seconds**.
- Full-size sequential showcase: `data/catalog-evaluation/full-render/catalog-1080.mp4` — 167.900 seconds / 5,037 frames, 1080×1920 H.264/AAC, 156,173,484 bytes. This preserves source speech and shows each treatment individually.
- Extended master: `demo-master/`, with a complete gallery at 55.0–93.4 seconds. Its local export is `data/reelos-hackathon-master-all-effects.mp4`, 193.4 seconds. The master grew by 13.4 seconds to include the full gallery at normal speed; this is not a claimed official portal duration.
- Editable recording preview: `http://127.0.0.1:3017/#project/demo-showcase`; the timeline now ends at 1:41.4. Earlier 75-second exports remain preserved.

Each gallery tile is 96 frames at 30 fps: 3.2 seconds at normal speed. Four play together, making twelve groups / 38.4 seconds. Gallery tiles are muted to avoid four overlapping speech tracks; the original-voice opening and original background score remain in the recording. The sequential portrait export retains the original speech. Text/cards/figures in the catalog demonstration are illustrative and are labelled that way; no engagement or personal metrics are claimed.

## Recording chapter map

| Recording time | Treatments |
|---|---|
| 20.0–23.2 s | 01 Noise; 02 Lineup; 03 Locked On; 04 Orbit |
| 23.2–26.4 s | 05 Lean In; 06 Backdrop Word; 07 Spotlight; 08 The Bill |
| 26.4–29.6 s | 09 Moody; 10 Swipe; 11 Todo; 12 Comment Box |
| 29.6–32.8 s | 13 Tap; 14 Pause Point; 15 Uninstall; 16 Reel Frame |
| 32.8–36.0 s | 17 Shortcut Rain; 18 Reject Stamp; 19 Countdown Flip; 20 Rabbit Hole |
| 36.0–39.2 s | 21 Cover Star; 22 Scribble; 23 Glass Widgets; 24 Red Collage |
| 39.2–42.4 s | 25 Split Headline; 26 Pastel Word; 27 Check Pills; 28 Timeline |
| 42.4–45.6 s | 29 Headline Box; 30 Profile Wall; 31 Tier List; 32 Broll Split |
| 45.6–48.8 s | 33 Phone Fan; 34 Dot Reveal; 35 Headline Wall; 36 Checklist |
| 48.8–52.0 s | 37 Liquid Glass Graph; 38 Carousel Spin; 39 Match Cut; 40 Apple Toggles |
| 52.0–55.2 s | 41 Led Sign; 42 Slow Push; 43 Over The Shoulder Zoom; 44 Messages |
| 55.2–58.4 s | 45 Place In Grid; 46 Glitter Spotlight · look; 47 Editorial Cover · look; 48 Glass Bento · look |

## Verification and provenance

The main app source, catalog source clone and current testing-video file have identical SHA-256 `f545a15ce3be8208c9dbf27aac93bfddc8d92af972ef337619461934d0f18dc5`. The local full sampler matches the live API export byte-for-byte (SHA-256 `6a8f4eb69e9caeb9a0ecbb589504794c901f764d0dbafe44a58d7ba665d9a99e`). The frozen manifest checks that the first 45 IDs match the entire catalog exactly; the last three identify the sparkle, editorial and bento look options.

All 48 gallery clips were checked for 432×768, 96-frame encoding. All twelve groups were visually inspected in both browser-rendered snapshots and actual final encoded frames. Labels, source/effect pairing, bounds and the final three looks were checked. The whole recording export decodes without errors. HyperFrames runtime/layout/motion/craft/audio checks pass; 31/31 measured text contrast checks pass. Composition-local media-start warnings are intentional and were checked against actual output timing.

Recording audio measures −17.6 LUFS integrated and −1.7 dBFS true peak. It was measured, not personally heard. The extension uses the earlier original score with a finite tail and fade; no new voice/music generation was used. The presentation does not claim that ReelOS provides music synchronization.

The gallery reuses actual verified catalog renders driven by SAM masks and the approved source. No new paid model calls were made; the ledger remains $75 reserved of the approved $75 local cap. Main v22 and catalog demo v1 are preserved. Nothing was published or submitted.

Recipes remain attributed to Vibha Ramprakash under MIT, with original notices retained in the application vendor inventory. Original Remotion artwork and original app workflow remain separately credited. EFFECT_GALLERY.json records every source interval, label, recipe/look and clip hash; prepare_effect_gallery.py rebuilds private clips from the verified sampler without changing editable HTML. Private media and renderer caches remain excluded from Git.
