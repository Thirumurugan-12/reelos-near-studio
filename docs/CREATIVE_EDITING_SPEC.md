# ReelOS creative editing specification

Version 0.1 · 26 October 2026 · Incorporates the user-supplied editing guide into the proposed product. This is a build specification; no effects or application code are implemented yet.

## 1. Product workflow

**Upload → direct → storyboard → render draft → revise → export.**

The creator uploads footage, optionally a reference and supporting assets, then describes the result. Muse analyzes the material and proposes a constrained edit. ReelOS displays the beat summary and renders a draft using supported operations. SAM supplies subject masks and tracking wherever foreground separation is needed. Revisions produce a new plan and output version.

The storyboard is an inspectable representation of the same validated plan that renders. It is not a separate model-authored document. Preview generation can proceed automatically; the creator can pause to adjust the plan. A creator who explicitly requests “show me the storyboard before rendering” gets a project-level review gate until they choose Render draft. Final export is explicit.

## 2. Direction controls

Provide one prompt field plus compact controls for style preset, headline, emphasis intensity, and output length. Optional reference input appears beside the source asset. Distinguish three origins: **preset**, **observed in reference**, and **user override**. Supported reference observations should point to source evidence; inferred or unsupported details must not appear as exact recovered settings.

The first preset is **Creator explainer**: readable bold headline, restrained entrance motion, a subtle background spotlight, and a short tracked label. It uses the three P0 primitives rather than introducing additional effects.

## 3. Storyboard contract

Each beat displays output start/end, source start/end, transcript text when available, visible treatment, subject, and operation IDs. Transcript text is verbatim only when supported by transcription; other text is labelled a proposed headline or summary. Explain creative intent in one short sentence.

Illustrative 20-second edit:

| Output time | Treatment | Operation | Purpose |
|---|---|---|---|
| 0–3s | Two-line headline partly behind the speaker | Behind-subject text | Establish the topic |
| 3–8s | Subtle background dimming | Subject spotlight | Emphasize the explanation |
| 8–12s | Label following selected subject | Tracked label | Reinforce the named idea |
| 12–20s | Clean source footage | Base clip | Let the conclusion breathe |

These are illustrative timings, not automatic defaults for every video. The source interval depends on the actual footage.

## 4. Style and motion system

Use a reusable style object referenced by effect instances. Instance overrides win over reference-derived parameters, which win over preset defaults. Freeze resolved values in each edit version so later preset changes cannot alter old exports.

| Parameter group | Required fields |
|---|---|
| Canvas | Width, height, fps, safe content bounds |
| Typography | Resolved font asset ID, weight, relative size, line height, alignment |
| Palette | Text, accent, background, outline colors |
| Layout | Normalized anchor, maximum width, safe-region policy |
| Entrance/exit | Supported animation ID, duration in seconds, easing ID, offset |
| Subject treatment | Subject ID, layer, feathering policy, bounded intensity |
| Provenance | Preset ID/version, reference observation IDs, explicit overrides |

Adapt the supplied recipes into a reference look at 1080 × 1920: off-white `#F4F4F2` headlines; optional coral `#D97757` accent; two headline lines near 20% and 27% frame height; upward entrance offset of 2% frame height; cubic ease-out. The guide specifies 12-frame entrances and a 4-frame stagger. Our explicit 30 fps interpretation is 0.4 seconds and approximately 0.133 seconds; the source project's actual fps is unknown.

Treat exact named fonts as optional assets requiring availability and licence checks. A bundled, licensed substitute is acceptable when disclosed. Fit long text by wrapping or adjusting within bounds, never by cropping silently. These are rendered-video styles; ReelOS's application UI keeps its separate design system.

## 5. Effects catalog

The guide's fourteen sections become a workflow feature plus thirteen catalog entries. The existing SAM spotlight is an additional ReelOS effect. Catalog metadata includes stable ID, parameters, dependencies, layer order, revision intents, implementation status, and priority. Only implemented, validated entries are selectable or planner-eligible.

| ID | Feature | Parameters and behavior | Dependency / release |
|---|---|---|---|
| `storyboard` | Beat plan | Readable view derived from canonical operations | P0 workflow |
| `behind_subject_text` | Text behind speaker | Text lines, anchor, scale, color, entrance, stagger; foreground covers letters | SAM masks; P0 |
| `subject_spotlight` | Subject spotlight | Background dim/desaturation, feather, fades; preserve foreground | SAM masks; P0 |
| `tracked_label` | Tool/subject label | Label, tracked anchor, bounded offset; optional supplied icon | Subject geometry; P0 text, P2 icon reveal |
| `active_word_captions` | Highlighted captions | Up to three words, active-word accent box, shadow, safe position | Verified word alignment; P2 |
| `repo_card` | Repository card | Owner/name, supplied or verified description and dated counts | Asset/data provenance; P2 |
| `prompt_bar` | Animated prompt | Text, typing interval, bar and button treatment | Vector graphics; P2 |
| `grade_reveal` | Color wipe | Grade preset, reveal direction, line width, easing | Two image treatments; P2 |
| `magazine_cover` | Magazine composition | Masthead, frame, cover lines, optional barcode asset | SAM masks and template; P2 |
| `screenshot_overlay` | Actual screenshot | Asset ID, width, anchor, radius, shadow, fade | Uploaded asset; P1 if schedule permits |
| `shot_transition` | Whip or nested zoom | Supported subtype, duration, transform, bounded blur | Multiple-shot timing; P2 |
| `moody_grade` | Grade and optional control graphic | Bounded grade preset; graphic states tied to actual changes | Renderer filters; P2 |
| `reel_grid` | Wall of reels | Up to nine supplied clips, grid order, reveal timing, per-tile crop | Multi-asset decoding; P2 |
| `pause_explain` | Freeze and explain | Freeze source time, hold duration, small/large bounds, resume point | Explicit audio and time remapping; P2 |
| `jump_cuts` | Remove pauses | Silence threshold, protected speech intervals, alternating crop | Verified speech boundaries; P2 |

Optional guide-inspired starting values include 1.15× alternating crop for jump cuts, 0.22 seconds as a configurable pause threshold, and 6-frame whip entrance/exit at an explicit timebase. They require footage tests before adoption. Freeze effects must specify whether audio pauses, continues, or switches to a separate narration asset; do not infer this from a visual recipe.

## 6. Meta orchestration and execution

1. Probe and normalize media; identify shots and valid time ranges.
2. Run Muse footage analysis and optional reference observations.
3. Obtain transcript/turn timing when enabled; obtain verified word alignment only for features that require it.
4. Resolve subject selection and SAM masks for required intervals. Reset tracks across cuts.
5. Planner selects only available catalog entries and resolves style values.
6. Validate assets, timing, text, layers, parameters, and dependency artifacts.
7. Derive storyboard; honor explicit review mode if selected.
8. Render preview and inspect representative compositing frames during development.
9. Apply revisions as constrained plan patches; reuse unchanged artifacts.
10. Export from the same frozen plan at final resolution.

Meta models propose meaning, choices, and perception results. Rendering code owns exact timing, easing, typography, compositing, and encoding. Retain the Python/FFmpeg baseline; the guide's Remotion usage remains a bounded architecture evaluation rather than a second required engine.

## 7. Conversational controls

| Creator request | Expected change | Protection |
|---|---|---|
| “Put the title behind me” | Use background text layer and subject mask | Preserve text, clip timing, and audio unless specified |
| “Move the headline lower” | Adjust normalized vertical anchor within safe bounds | Reuse masks; preserve headline wording |
| “Make the spotlight softer” | Reduce dimming and/or increase allowed feathering | Preserve source selection and other effects |
| “Make the opening faster” | Tighten permitted leading trim and opening effect durations | Preserve speech boundaries; no hidden speed change |
| “Match the reference's headline color” | Update supported text color with reference evidence | No claim of full style reproduction |
| “Highlight each spoken word” | Enable caption recipe only after alignment support exists | Otherwise explain limitation and offer supported turn-level emphasis |

Show a concise change summary before or alongside the new draft. Unsupported catalog entries cannot be silently approximated as completed. Preserve the last successful render when a revision fails.

## 8. Acceptance gates

- A preset produces identical resolved styling for equivalent operation settings across preview/export.
- Storyboard operation IDs and intervals match the validated plan exactly.
- Headline entrance is deterministic at the configured fps; foreground occlusion remains correct during movement.
- Subject loss hides dependent graphics or asks for correction; it does not attach them to another person silently.
- Targeted changes preserve unrelated fields and reuse masks when appropriate.
- Word-level effects remain unavailable until verified alignment exists.
- UI exposes available features only; future catalog entries are documentation, not simulated working controls.
- User-uploaded assets retain provenance; template copy never fabricates facts, metrics, or screenshots.

## 9. Build order

Deliver P0 storyboard/style contracts with headline, spotlight, and tracked label. Then validate reference mapping and, if practical, screenshot overlays. Select at most two P2 additions after P0 passes. Captions require alignment first; transitions, grid layouts, and freeze sequences require expanded media/timing contracts. The full catalog is a roadmap, not a ten-day delivery commitment.
