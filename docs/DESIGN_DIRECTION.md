# ReelOS design direction

Prepared 26 October 2026. Companion to [the PID](REELOS_PID.md).

## Status

The user supplied nine design inspiration collections. They are the reference pool for future design work. The direction below is a proposal, not an approved visual design or a claim that particular examples have been selected. Collection pages were reviewed for their scope; individual designs and interactions still need visual inspection before adopting specific patterns.

## Product character

A calm editing studio with expressive video content. The creator's footage supplies most of the color and movement. The surrounding interface makes assets, editing decisions, and revisions easy to understand.

Prioritize the actual workspace over a marketing landing page for the hackathon. An impressive finished edit and a clear revision flow should carry the presentation.

## Reference pool

| Collection | Intended use in ReelOS | Review status |
|---|---|---|
| [Minimal Gallery](https://minimal.gallery/) | Explore restraint, typography, and clear content hierarchy | Collection page accessible |
| [Detail](https://detail.design/) | Inspect small interaction, copy, and accessibility decisions | Collection page accessible |
| [Navbar Gallery](https://www.navbar.gallery/) | Explore compact project navigation and secondary actions | Collection page accessible |
| [CTA Gallery](https://www.cta.gallery/) | Explore primary action prominence and specific action labels | Collection page accessible |
| [404s](https://404s.design/) | Reference for missing-project and recovery states | Page inaccessible during review; examples not evaluated |
| [MaxiBestOf](https://maxibestof.one/) | Explore typography and art direction for project identity | Collection page accessible |
| [SEESAW](https://www.seesaw.website/) | Find relevant design-tool and productivity interfaces | Collection page accessible |
| [A1 Gallery](https://a1.gallery/) | Additional visual exploration | Page inaccessible during review; examples not evaluated |
| [Supahero](https://supahero.io/) | Optional launch-page composition after the workspace works | Page accessible; announces it is now part of ScreensDesign |

These are starting points for research, not copied layouts or endorsements of individual designs.

## Proposed workspace

- **Header:** ReelOS wordmark, editable project name, save/job state, version access, Export.
- **Asset area:** Source and reference thumbnails, duration, upload status, and subject-selection access.
- **Stage:** Largest visual area, portrait preview, playback controls, elapsed time, Original/Edit toggle.
- **Direction panel:** Initial prompt, concise editing observations, revision input, and a clear summary of the latest changes.
- **Bottom strip:** Effect intervals and version selection. Keep this lightweight until the PID calls for a fuller editor.

Default to the current edited result once it exists. Preserve playback position where feasible when comparing versions. Show a pending revision separately until its preview is ready; never replace a playable result with a loading placeholder.

## Proposed visual foundations

These values are initial design choices to test with real footage.

| Element | Starting direction |
|---|---|
| Canvas | Warm near-white, `#F5F4F0` |
| Panels | White, `#FFFFFF` |
| Preview surround | Near-black, `#191919` |
| Main text | `#20211F` |
| Secondary text | `#60635C` |
| Dividers | `#DEDFD8`; use stronger boundaries when necessary for control visibility |
| Primary action | Deep green, `#244A39`, with white text |
| Typography | One readable sans-serif family; tabular numerals for timing |
| Type sizes | 12px metadata, 14px controls, 16px body, 24px page title |
| Spacing | 4px base; 8, 12, 16, 24, 32px steps |
| Corners | 6px controls, 10px panels; pills only for short statuses |
| Depth | Fine borders; modest shadow for overlays and dialogs |

Verify text, controls, focus rings, and disabled states for contrast in implementation. Decorative dividers do not establish the accessibility of an input boundary.

## Action hierarchy and copy

The [creative editing specification](CREATIVE_EDITING_SPEC.md) adds a storyboard view and reusable style controls. Place the beat summary beside editing decisions, with a compact style selector and optional overrides. An explicitly enabled storyboard review mode exposes Render draft; ordinary projects continue automatically to preview. Show only implemented effects. Keep the rendered video's template palette independent of the application palette.

One primary next action per stage:

1. Empty project: **Upload footage**.
2. Footage ready: **Create draft**.
3. Revision entered: **Apply changes**.
4. Draft accepted: **Export video**.

Supporting copy should describe consequences: “Lowered the headline. Reduced background dimming.” Use “Tracking the selected person” for a running stage. Display a percentage only when measured progress exists. Keep model/request details in an optional technical evidence panel.

Recovery examples:

- No match: “We couldn't find a person in this shot. Select a person in the preview or choose another clip.”
- Render failure: “This revision couldn't finish. Your previous edit is ready to play.” Provide Retry and error details where useful.
- Missing project: “This project isn't available.” Provide a return to projects and a create-project action.

## Interaction and accessibility

Use short transitions for panel changes and clear playback feedback. Honor reduced-motion preferences. Avoid animation that competes with the footage or hides processing time.

Keyboard users must be able to upload, select a subject through an equivalent accessible control, play/pause, seek, compare versions, revise, and export. Include visible focus and labelled controls. Do not use color alone to distinguish source, effects, or job state. Announce processing stage changes without repeatedly interrupting assistive technology.

At wide sizes, show assets, preview, and direction together. At intermediate sizes, collapse assets into a drawer. On mobile, stack preview, direction, and assets in task order. Verify at 320, 768, 1024, and 1440px with real text and footage.

## Design review gates

Before implementing the final visual treatment, select and visually inspect three concrete examples: workspace hierarchy, revision interaction, and navigation/action hierarchy. Record the borrowed principle and why it helps the creator; retain ReelOS-specific structure and copy.

Before demo freeze, verify the empty, processing, subject-selection, draft-ready, revising, export, and failure states. The preview must remain prominent, the next action obvious, and the previous output recoverable. Inspect both short and long project names and error messages.

No website, mockup, or interface has been built by this document. It records references and a proposed direction for the next design step.
