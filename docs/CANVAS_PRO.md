# Canvas Pro live workspace

Implemented 1 November 2026 after approval of design option 01. This replaces the live frontend at port 3000; the ten-option design board remains a separate prototype.

## Interaction and visual system

Graphite surfaces, lime primary actions, rounded buttons, Archivo Black display type, Montserrat interface labels, Inter forms and Space Mono time markers. Fonts are self-hosted with retained licences.

The workflow is footage → direction → preview → revision → export. Edit, Looks and Media share one contextual inspector. Desktop shows the inspector beside the canvas; mobile opens a modeless bottom sheet with an explicit close action, Escape handling and focus return. Creative direction remains mounted while tools change so unsent instructions survive switching tools.

A compact timeline packs non-overlapping effects into shared lanes and separates overlapping effects. Selecting a moment seeks the actual video and opens its details; the native moment selector gives small screens access to all 48 moments. A targeted revision prefixes the selected effect ID in the existing revision request. Quick treatments open actual catalog settings, with placement starting at the playhead. The 48-effect limit is explained before submission.

Original/edit playback, upload, subject selection, storyboard review, catalog assets, preview generation, version restore and MP4 export retain the existing backend contracts. Version history uses a native dialog. Failed jobs and upload failures remain visible and dismissible. Usage details remain accessible in the footer.

## Validation

- Frontend TypeScript check and two timeline tests passed. Tests cover overlaps, touching boundaries, input preservation and a 48-moment single-lane case.
- Production Docker frontend build succeeded and the frontend container was deployed without restarting the backend.
- Real browser checked at 320×740, 390×844, 768×1024, 1024×768 and 1440×900. Document dimensions matched the viewport; timeline and inspector bounds fit. Long controls scroll internally.
- Real source upload, rejected undecodable upload, error dismissal, preserved instructions across tools, original/edit comparison, video seeking, history selection and restore were exercised.
- A real three-second Backdrop Word preview rendered from the catalog through the live UI using cached tracking. Demo version `69a2d3ffc8944beaa5c03bb33a2e09be` is retained in history. The full 167.9-second catalog demo was restored as current afterward.
- Mobile sheet close focus, Escape return and the full-catalog placement guard were checked.
- Evidence is local under `data/canvas-pro-checks/`: desktop.png, mobile.png and sheet.png. User media is not committed.

## Scope

This is the editing workspace redesign, not a new rendering engine. It uses native video controls and approved effects; timeline dragging, freeform trimming and a full professional NLE are not added. No fresh paid Muse planning request was made for this UI verification. Creator usability evaluation remains deferred at the user’s request.

## Title headroom follow-up

Edit now has explicit Room for titles / Original framing controls and first-failed-plan recovery selection. Both preserve immutable history and use the shared API/CLI renderer. [Verified recovery outputs and limits](TITLE_LAYOUT_RECOVERY.md).
