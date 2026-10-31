# Full 45-effect catalog implementation

Scope: adapt all 45 MIT-licensed starter recipes from Vibha Ramprakash's claude-video-effects, including aliases and its three additional named looks. Retain attribution and original fonts/licences. Reuse the actual recipe functions; replace upstream MediaPipe/CLI/private-code hooks with ReelOS's validated timeline, SAM tracking and safe project assets.

1. Freeze upstream source; inventory all 45 recipes/options and licences. No MediaPipe model download or setup-script execution.
2. Add a bounded catalog-effect contract, aliases/named looks, per-recipe option validation, safe media asset IDs and regression tests. Legacy plans serialize/render unchanged.
3. Bridge the upstream renderer to SAM masks and derived head anchors. Preserve camera ordering, foreground occlusion, freeze-frame semantics, deterministic motion, and source audio. Add source/supporting media cards with explicit provenance.
4. Add image/video supporting uploads, catalog discovery/apply endpoints, CLI/skill commands, Muse planning/revision schema and an accessible catalog UI with preview assets and editable options. No arbitrary model code or filesystem paths.
5. Render every recipe and named look at preview/export sizes, inspect start/middle/end and moving-subject frames, fix runtime/geometry problems. Export an audio-preserving full catalog demonstration on authorised source footage.
6. Build/deploy Compose safely with no active jobs, verify browser/mobile integration and legacy exports, document reuse, limitations and per-effect evidence. Only call all 45 implemented after this verification.

Acceptance: 45 distinct renderers reachable through UI/API/CLI/Muse; real SAM rather than upstream segmentation; safe supplied images/clips; explicit demo data versus real user statistics; tested named looks and aliases; seek-safe still checks; immutable versions; preserved legacy schema/audio. Missing optional assets use explicitly labelled source-frame cards, never invented external screenshots.

