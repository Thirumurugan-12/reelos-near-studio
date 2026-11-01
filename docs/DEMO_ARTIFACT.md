# Local hackathon demo MP4

## Canvas Pro refresh — 1 November 2026

The current review artifact is `data/reelos-hackathon-demo-canvas-pro.mp4`: **75.000 seconds, 1920 × 1080, 30 fps, 2,250 frames, H.264/AAC, 26,559,617 bytes**. It replaces the earlier workspace/media/history images with actual Canvas Pro browser captures. The earlier `data/reelos-hackathon-demo.mp4` is preserved as historical evidence.

Full HyperFrames check passed with zero runtime/layout/motion/craft/audio errors and **25/25 contrast checks**; the same nine intentional scene-local media warnings remain. Actual encoded frames at 10 and 53 seconds were inspected. The entire file decodes without error. Decoded PCM SHA-256 matches the previous demo exactly (`f3b9c978c3336f980f6b000068be0c43ab3ccacf076f10b5ed0d58b4d531aaa2`); no new listening claim is made. Delivery render took 26.4 seconds, measuring presentation rendering only.

The captures show rehearsal project `5988d17cb3a34cf2967a0b442c6d6936`, its existing source/reference, current baseline v1 and retained revision v2. Selecting v2 for its capture did not restore it or change the durable baseline. Asset hashes and capture descriptions are retained in `demo-showcase/ASSET_LEDGER.json`. Verification logs/frames are ignored under `data/completion-audit/`. No model calls, external publication or submission occurred. Portal requirements, creator feedback and human listening review remain open.

## Historical 30 October artifact

Verified 30 October 2026. The composed walkthrough is ready for local review; nothing has been published or submitted. Current portal requirements, creator feedback (deferred by the user until the end) and human listening review remain open.

## Artifact

- Local file: ignored `data/reelos-hackathon-demo.mp4`.
- Actual encoded output: **75.000 seconds**, **1920 × 1080**, **30 fps**, **2,250 video frames**, H.264/AAC, **26,503,116 bytes**.
- Final render: HyperFrames 0.8.220, delivery profile, 22.6 seconds on the current machine's hardware capture path. This measures presentation rendering, not ReelOS model/edit latency.
- Editable source: `demo-showcase/`. Managed local preview: `http://127.0.0.1:3017/#project/demo-showcase`, bound to 127.0.0.1 and checked to return HTTP 200.

The presentation shows real original/edited footage, actual workspace captures, the actual selected SAM thumbnail, real retained parent/revision previews, recovery state and the full 167.9-second export. Saved results are visibly labelled as previously generated. It does not simulate model generation, invent UI controls, or present a montage as a live generation recording.

The main full-length video and selected project remain unchanged. The walkthrough's short output excerpts are explicitly demonstration material; its full-duration claim refers to the separately verified 2:47.9 source export.

## Verification

- Full HyperFrames browser check passed: zero runtime, layout, contrast, motion, craft and audio errors; contrast samples passed. Nine lint warnings document intentional scene-local media starts.
- Scene/phone/transition sheets were inspected. A fresh review found three P1 issues in UI readability, subtle revision visibility and history evidence; actual regions were enlarged and re-inspected after corrections. [Review record](../demo-showcase/REVIEW.md).
- The editable browser preview played through to 75 seconds and stopped at 01:15/01:15.
- The final MP4 decodes completely with FFmpeg without errors. Actual encoded frames were sampled, including the magnified revision and the copy naming Muse Spark, SAM and Remotion.
- Local audio measurement: **−14.3 LUFS integrated**, **−1.7 dBTP**, **zero clipped samples**. Short inter-note rests and the final score fade are expected. Sound was measured, not personally heard.
- The score is an original deterministic local composition in `demo-showcase/compose_audio.py`; source speech is demonstrated in the opening. No new paid Meta or media-generation requests were used. The presentation's sound bed is not an app music-sync feature.

Private raw footage, clips, captures, score WAV, render history and media cache are excluded from Git. Source code, the asset-hash ledger, source/rights context and reproducibility instructions are retained. Existing Meta reservations remain $46 against the configured $50 cap; the known-usage estimate is $1.20548550 with two historical unpriced calls. Neither figure is confirmed account billing.

## Remaining submission gates

Verify the current portal's duration/file/access requirements, gather actual creator task feedback, listen to the final audio and review the presentation before external publication. The 75-second duration is a local preparation choice, not a claimed official limit. No public hosting, social publication or hackathon submission has been performed.
