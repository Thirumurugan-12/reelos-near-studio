# ReelOS Canvas — proposed direction

31 October 2026. Design exploration only; the working editor and backend remain unchanged. `index.html` is an original interactive concept, not a finished production implementation. Its video playback uses the existing local catalog sampler. Prototype controls are explicitly labelled, make no paid calls, and do not upload or mutate project data.

## All nine references supplied by the creator

| Source | Proposed use |
|---|---|
| [minimal.gallery](https://minimal.gallery) | Product composition and visual restraint; Diffusion Studio is the relevant new example. |
| [detail.design](https://detail.design) | Contextual controls, clear feedback and subtle interaction polish. |
| [navbar.gallery](https://navbar.gallery) | Compact desktop tool rail and mobile tool bar. |
| [cta.gallery](https://cta.gallery) | One primary action for each stage. |
| [404s.design](https://404s.design) | Recoverable empty/error states; site could not be retrieved during this review. |
| [maxibestof.one](https://maxibestof.one) | Typography, application layouts and product presentation. |
| [seesaw.website](https://seesaw.website) | Creative-tool references, particularly Atlas. |
| [a1.gallery](https://a1.gallery) | Broad visual exploration; site could not be retrieved during this review. |
| [supahero.io](https://supahero.io) | Specific Weavy and Linear visual references. Its page now says it is part of Screensdesign. |

## Selected new references

- [Diffusion Studio on Minimal Gallery](https://minimal.gallery/diffusion-studio-2/): video/motion workspace, preview hierarchy and tool grouping. The gallery entry was published 20 May 2026. Inspected the actual reference image, not only its text.
- [Linear on Supahero](https://supahero.io/hero/linear): dark surface hierarchy, concise controls and strong content priority. This gallery capture is dated 30 October 2024; not a claim about its current app interface.
- [Atlas on SEESAW](https://www.seesaw.website/websites/atlas-for-mac), [product site](https://atlasformac.com): thumbnail-led media library. Inspected the actual library image on the product site. Gallery entry dated 22 September 2026.
- [Weavy on Supahero](https://supahero.io/hero/weavy): output-led creative composition and restrained accent. Its gallery capture is dated 29 September 2025. The current weavy.ai redirects to Figma Weave; we are referencing the archived gallery image. Do not copy its node workflow into a mobile editor.

These galleries mostly show marketing websites. Their visuals inform the proposal; the ReelOS editing workflow below is our own adaptation, not a claim that any reference implements it.

## Review of the current product

Context: mobile-first web editor, existing visual tokens can be replaced; primary user task is getting an intentional video edit from footage and a brief. Reviewed usability and microcopy with the UX design review skill. No conversion/payment surface; dark-pattern lens not applicable. A full WCAG audit is outside this direction-selection pass.

Major issues:

1. **Competing panels and oversized page chrome** (heuristics 6, 8). Assets, direction, catalog, timelines, status, project names and version controls all demand attention. Video is displaced. Put the preview in a stable canvas, tool navigation at its edge, and settings in a contextual inspector.
2. **Navigation describes storage/UI sections rather than the editing journey** (heuristics 2, 6). Five mobile tabs hide the relationship between briefing, previewing and adjusting. Use guided creation, then a stable editor with Edit, Looks and Media tools. Keep playback visible when opening a mobile sheet.
3. **A recipe catalog overwhelms first-time editing** (heuristics 7, 8). Forty-five descriptions are presented as a long list. Begin with a few visual directions, then reveal the full categorized library on demand. Recipes remain individually available; a named overall look would need an explicit, tested composition in production.
4. **Version history and technical state dominate** (heuristics 1, 8). Long version labels and persistent elapsed-time banners distract after work completes. Keep active processing feedback near the preview, collapse completed status, and move versions into a history drawer. Preserve the immutable version model.

Microcopy changes:

- “Creative direction” → “What should this edit feel like?”
- “Apply changes” → “Generate preview” for a request that renders a result; selected-effect changes should name the affected moment.
- “Storyboard” → “Your edit” for the compact timeline; use clear effect names inside it.
- “Local API allowance reserved” → secondary usage details in settings, while preserving the distinction from provider billing.
- Remove workspace slogans and large promotional headings inside an active editor.

Existing strengths to retain: source/edit comparison, full-video default, immutable versions, optional reference assets, original speech, real effect rendering and working exports.

## Proposed design and flow

Graphite canvas `#111214`, raised panel `#1A1B1E`, off-white text, lime primary action `#E9FF7B`, 4px spacing units, modest radii, and a system/Inter sans hierarchy. A single accent identifies primary actions and selections; shape, labels and focus outlines also convey state.

**Flow:** projects → upload footage → concise brief + optional reference + full/excerpt choice → generate preview → review → adjust selected moment or overall direction → export.

Desktop: compact 64px header, 72px tool rail, central persistent video, 176px two-track timeline and one 320px contextual inspector. No giant marketing heading or permanent completed-job banner. Version history is a drawer. Timeline uses grouped tracks rather than one row per effect.

Mobile: 56px header, persistent preview, compact timeline, fixed Edit/Looks/Media toolbar and modeless bottom sheets for controls. Entire document fits the viewport; sheets scroll internally. The software keyboard needs a separate implementation check before shipping.

Top three priorities: (1) establish preview and timeline hierarchy, (2) separate first-edit setup from subsequent editing, (3) replace the long catalog list with visual browsing and contextual controls. Full accessibility, timeline gestures and touch target review should accompany production implementation.

## Prototype and verification

Preview at [localhost:3018](http://127.0.0.1:3018). The isolated server serves only `data/design-concept`, not the repository or secrets. The code source is this folder's `index.html`; creator footage and captures remain ignored under `data/`.

To recreate locally, copy the HTML into `data/design-concept/`, place an authorized portrait still there as `footage.jpg`, start the real app on port 3000, then run `python3 -m http.server 3018 --bind 127.0.0.1 --directory data/design-concept`.

The prototype tests layout and interaction affordances, not real generation or uploads. Production work would reuse the existing validated services and add categorized effect browsing, version drawer, grouped selectable tracks and contextual effect editing. Current revisions cannot add arbitrary new placements through chat; wire that explicitly rather than imply the proposal already supports it.

Checked in the real browser at 320×844, 390×844, 768×900, 1024×900 and 1440×900: document size equals viewport size. Tested the Upload → Brief → example edit flow, mobile Looks sheet, close controls, and timeline selection affordances. No console errors were captured. Desktop/mobile proof images are `data/design-concept/desktop.png` and `mobile.png`. This is a visual/interaction prototype, not a full accessibility or production workflow certification.
