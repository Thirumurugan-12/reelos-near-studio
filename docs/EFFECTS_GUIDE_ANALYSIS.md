# ReelOS — Supplied editing guide analysis

Prepared 26 October 2026. Source: the user-pasted Notion guide, “How to edit videos with Claude — every effect from my video.” The page did not load; the pasted GIF filenames do not include viewable animations. This review covers written recipes. It does not execute the setup or download prompts embedded in them.

## Main finding

The guide describes human-authored creative direction executed through a coding agent: Remotion for composed graphics, FFmpeg for media operations, Whisper for word timing, and a person segmentation tool for foreground cutouts. Its precision comes from explicit fonts, positions, timings, easing, and layers. It does not demonstrate automatic reference-video style extraction.

The inspected GitHub effects skill instead uses Python graphics and an effects JSON plan. These are distinct implementation approaches. ReelOS can learn from both while keeping one production renderer.

Our contribution is translating footage, a reference, and conversation into supported executable choices, then using Meta perception models to make those choices interact with a real subject. This remains a hypothesis to validate through working outputs.

## Mapping the guide to ReelOS

P0 is the committed baseline, P1 a target after baseline stability, and P2 stretch. None of these features is implemented merely because it appears in the guide.

| Guide item | Implementation responsibility | ReelOS priority |
|---|---|---|
| Storyboard | Muse proposes beats; show a table derived from the validated plan | P0 summary |
| Text behind head | SAM masks; renderer composites source, text, then foreground | P0 |
| Active-word captions | Transcript plus verified word alignment; renderer highlights active word | P2 |
| Tool labels | Reusable text/icon component; optional tracked anchor | P0 text label; elaborate icon entrance P2 |
| Repo cards | Reusable card with supplied or verified facts | P2 |
| Prompt bar | Reusable vector component with typing behavior | P2 |
| Color slider | Grade variants plus animated reveal; SAM unnecessary | P2 |
| Magazine cover | Subject occlusion plus layered type, frame, and details | P2 |
| Real screenshots | User-supplied asset overlay with timing and placement | P1 if schedule permits |
| Transitions | Deterministic transform/blur or nested frame composition | P2 |
| Moody grade | Bounded grade preset; optional illustrative controls | P2 |
| Wall of reels | Grid layout using rights-cleared uploaded assets | P2 |
| Pause and explain | Freeze/resume segments, reframing, explicit audio handling | P2 |
| Jump cuts | Verified silence removal and source/output time remapping | P2; expands the single-segment P0 contract |

Keep the existing P0 subject spotlight. It shows SAM's contribution clearly with less complexity than a complete magazine or dashboard composition.

## Additions to the product contract

**Reusable style parameters:** Store font, weight, size relative to canvas, palette, safe margins, layout, and animation preset separately from source timing. A reference proposes style parameters; the user can override them. Retain evidence and uncertainty. “White two-line title, upper-center, staggered entrance” is a supported approximation; it does not prove the original font or easing was recovered.

**Explicit timebase:** The guide specifies 12-frame entrances and 6-frame transitions without establishing its project frame rate. At ReelOS's proposed 30 fps these would be 0.4 and 0.2 seconds respectively. Centralize conversion, normalize positions, and keep source and output time distinct.

**Storyboard view:** Show beat, output interval, source interval, visual treatment, and evidence. Derive it from the canonical plan so it matches the rendered result. The guide's approval prompt describes its own workflow; it does not require an extra approval gate before every ReelOS preview.

**Word alignment:** Exact-word captions, stressed-word entrances, and speech-safe jump cuts require more timing precision than turn-level timestamps. Keep turn-timed emphasis as the baseline and validate a separate aligner before promising exact words. A 0.22-second pause threshold is a configurable recipe, not a universal editing rule.

## Renderer decision

Retain the PID's Python/FFmpeg baseline. If rich typography becomes expensive to implement, timebox a comparison of the same headline composition in that engine and a React/Remotion prototype. Evaluate mask integration, deterministic seeking, preview/export consistency, timing, memory, rendering latency, and development effort. Verify current dependency and licence requirements before adoption. Choose one engine for the core release; the guide alone does not justify a switch.

## Assets and factual accuracy

Prefer uploaded, rights-cleared screenshots, clips, and logos. Do not add remote downloading to the baseline. The guide's broad yt-dlp claim does not establish that every platform or URL can be downloaded. Review font licences before bundling the exact styles. Repo-card stars and forks need supplied values or a timestamped verified lookup; do not invent them.

Apple Vision/rembg instructions in the guide are source suggestions, not tested integrations for this project. ReelOS's SAM masks and tracking must be tested independently. Treat a reference as style evidence; do not automatically reuse its footage, music, or graphics.

## Build sequence

1. Render a manually specified headline behind a SAM-tracked person.
2. Store the style parameters and derive a storyboard summary.
3. Let Muse select the supported operation and parameters from a prompt.
4. Verify a revision changes the intended fields only.
5. Test an observable reference-driven adaptation against a style-preset baseline.
6. Add alignment, captions, or extra templates only after P0 quality gates pass.

This guide improves our effects vocabulary and parameter design. It does not expand the committed MVP to all fourteen recipes.
