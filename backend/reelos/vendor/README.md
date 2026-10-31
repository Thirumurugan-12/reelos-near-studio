# Attributed 45-effect renderer

Adapted from https://github.com/Vibha-Ramprakash/claude-video-effects
by Vibha Ramprakash, MIT licensed; see LICENSE.claude-effects.txt.
Inspected commit: 99c9a3393ee14d39bea155a05c73dc069f02f16f.
Original scripts/fx.py Git blob: 4058ef7c256b7cf1968c63d7dd45a79526849fdf.

Retained all 45 actual drawing implementations and three named looks. Removed the
upstream CLI, file loading, MediaPipe segmentation, executable private hook and setup
script. ReelOS supplies validated options, project-scoped media, SAM masks and timing.
A small local YuNet detector anchors effects to the face inside the selected SAM mask;
when a face cannot be detected, a SAM head estimate is used. Missing tracked people
suppress subject-dependent effects. Original audio is unaffected by visual recipes.

Adaptations include a bounded font cache, replacement of default attribution graphics
with ReelOS/neutral labels, source-derived media cards, safe metrics requirements,
and deterministic frozen/source avatar frames. This is reuse of the MIT recipe library,
not a claim that ReelOS originally authored these effects. These remain starter recipes.

Fonts are unmodified upstream assets with bundled notices in fonts/. Full additional
Anton and Montserrat OFL texts are retained. models/yunet.onnx is the upstream
OpenCV Zoo YuNet model (MIT licence alongside it). No MediaPipe model is bundled.

Regenerate effect metadata with backend/scripts/build_effect_catalog.py. Build the
illustrated, explicitly fictional previews with render_catalog_previews.py. User
footage, SAM masks, and evaluation outputs stay outside this directory and Git.
