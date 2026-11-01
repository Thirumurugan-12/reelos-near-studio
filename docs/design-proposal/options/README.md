# Ten ReelOS design directions

Original interactive design explorations, 31 October 2026. Built in response to the creator's request for ten alternatives to the first Canvas proposal. These vary information architecture and editing flow as well as typography, palette and density.

Preview [the gallery](http://127.0.0.1:3018/options/) or [the compact comparison](http://127.0.0.1:3018/options/?board=1). Every tile opens a full-size responsive concept. The real ReelOS frontend/backend are unchanged.

| ID | Concept | Editing model | Main tradeoff |
|---|---|---|---|
| 01 | Canvas Pro | Preview + compact timeline + inspector | Familiar, balanced; still needs progressive disclosure on small screens. |
| 02 | Paper Edit | Story outline and editorial notes | Calm narrative planning; less efficient for precise effect timing. |
| 03 | Director | Conversation beside the preview | Best fit for natural-language editing; needs concise responses and visible change summaries. |
| 04 | Pocket Studio | Portrait stage with reachable tool dock | Strongest mobile direction; detailed controls belong in sheets. |
| 05 | Story Grid | Visual scene cards | Makes long recordings understandable; requires real scene grouping and scene selection implementation. |
| 06 | Script Cut | Script passage selection | Strong narrative control; accurate passage mapping is new work, not provided by the approximate transcript today. |
| 07 | Motion Lab | Spatial processing pipeline | Good for advanced demos and compositing; weaker as a default mobile workflow. The pipeline is illustrative. |
| 08 | Lookbook | Visual treatment browsing | Helps creators pick a style quickly; avoid allowing presets to replace editorial intent. |
| 09 | Cinema Focus | Large stage and floating prompt/tools | Excellent review focus; precision controls require a secondary surface. |
| 10 | Review Room | Before/after and keep/revise decisions | Builds confidence in results; better as a review mode than the only editor. |

Recommended shortlist: 01 for desktop structure, 03 for the conversational editing flow, 04 for mobile interaction. 08 and 10 could become optional modes inside that product rather than separate products.

## Scope and honesty

- These are UI concepts, not ten working video editors. Playback/export/generation buttons show concept feedback; they do not call models or mutate real project data. Brief dialogs and visual selection states are interactive.
- All concepts use the same authorized local still of an existing real ReelOS edit, to keep design comparison consistent. Review Room also uses a still from the unedited recording at the same source time. Creator footage remains outside Git.
- Scene timings, conversation, script passages and review notes are explicitly illustrative. Script text is an English paraphrase, not an exact transcript or synchronized caption track. Overall looks would need explicit, tested effect composition in production.
- These are original adaptations of the previously reviewed design references, not copies of ten external products. Refer to the parent README for the nine supplied galleries and verified reference examples.

## Local preview

Copy index.html, app.js and styles.css into `data/design-concept/options/`. Put authorized `footage.jpg` and `original.jpg` in `data/design-concept/`; the existing effect-poster URLs use the working app on port 3000. Start `python3 -m http.server 3018 --bind 127.0.0.1 --directory data/design-concept` if the isolated preview server is not running. It serves only the concept directory, not the repository or secrets.

## Checks

- All ten individually checked in the real browser at 1280×800 desktop and 390×844 mobile. Document dimensions equal the viewport for editor pages; long content scrolls inside task panels. The gallery intentionally scrolls.
- Visually inspected all ten mobile designs and the complete desktop comparison. Fixed Cinema Focus's intrinsic-width clipping and mobile editorial heading spacing.
- No console errors observed in browser checks. `node --check app.js` passes. Native buttons, links, form controls and a dialog with focus return are used. This is not a full WCAG audit or production touch/keyboard usability certification.
- Proof screenshots are under ignored `data/design-concept/options/`; the full comparison is `data/design-concept/ten-designs.png`.

## Typography and button refinement — 1 November 2026

All ten concepts now use self-hosted licensed typefaces instead of a shared system-font treatment. `typography.css` defines the combinations: Archivo Black display headings for Canvas/Pocket, Instrument Serif Italic for Paper/Lookbook and selected narrative headings, Playfair Display for Story Grid/Script/Cinema, Montserrat for geometric UI text, Inter for longer UI copy, and Space Mono for Motion Lab and time labels. These font files and licences already live in `backend/reelos/vendor/fonts/`; copy the `.ttf` and notice files into `data/design-concept/fonts/` when recreating the isolated preview. No external font service is required.

Primary controls now combine tailored text, rounded silhouettes and decorative circular arrow/check details. Paper uses an editorial underline action instead of a filled box; tool rails use a selection mark; filter tabs and secondary text actions use underlines; playback/send controls are circular. Arrow details are hidden from assistive technology so button names remain clear. Focus outlines and reduced-motion behavior remain enabled.

The style layer is linked after `styles.css`. Copy it alongside the other prototype files. Rechecked all ten concepts at 390×844 and 1280×800; checked primary-button bounds, native brief-dialog interaction and keyboard focus return. Fixed Canvas Pro's stage sizing so its timeline remains visible after font loading. `node --check app.js` passes; no console errors observed. These checks are scoped to the prototype, not a complete accessibility certification.
