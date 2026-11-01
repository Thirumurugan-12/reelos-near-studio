# Ten-attempt short-workflow protocol

Registered 1 November 2026 before dispatch. This is a bounded technical reliability test, not creator preference, general video quality or cold-machine performance.

## Fixed sample and success condition

Order: main, loft, camera, loft, camera, main, loft, camera, loft, camera. Each attempt starts a fresh project and uploaded source asset. Use the existing authorized 20-second main derivative, MART PRODUCTION's 20-second loft derivative and Anna Shvets's 17-second camera derivative; rights records are in EVALUATION_ASSETS.md. Every stock output must visibly identify STOCK FOOTAGE and TECHNICAL TEST. No reference or additional assets are used. Two audio-bearing runs and eight silent-stock runs reflect this deliberately limited corpus.

An attempt passes only if upload/inspection, real SAM, real Muse planning, preview, 1080p export, successful HTTP download, supported timing/effect checks and entire-file decode all succeed. Plans must retain the full derivative (17 or 20 seconds) and contain the three P0 subject effects. Headline, spotlight and label intervals are explicitly directed; this tests executing supported instructions, not autonomous editorial choice. Source audio presence and duration must be preserved. Inspect actual sampled frames before claiming visual quality; a functional pass may still expose the camera case's known silhouette artifacts.

When SAM finds multiple people, stop for inspection of actual thumbnails and select the intended person. That user-selection phase is normal workflow, not a failure/retry. A resumed draft reuses only that project's already-completed SAM artifact. No cross-project tracking/speech cache is copied. Measure selection waiting separately; worker times exclude queue/inspection waiting. Do not call a partially warm host a cold benchmark.

## Failure and budget policy

Retain all ten scheduled slots and failures. Never replace a failed attempt with an extra success, repeat an unknown paid outcome, or change prompts midway to improve the score. Poll the same returned job ID; if dispatch outcome is ambiguous, inspect durable jobs before further action. Provider failures count against the workflow result. A budget or disk stop is incomplete evidence, not a pass.

Initial ledger: $51 conservative reservations, $1.30135175 known-usage estimate, five unpriced calls; local cap $75. Expected calls: 10 SAM + 10 Muse + 2 speech = 22 additional $1 reservations, leaving $2 for unexpected allowance. No paid repair retries are planned. Check the actual ledger before each dispatch and stop before the cap; do not raise it automatically. No confirmed-billing claim is made.

Private run state, actual subject thumbnails, outputs and verification logs live under ignored `data/reliability/`. A one-off API driver retains each request/job marker and refuses to overwrite prior discovery state. Neither a fresh API access smoke call nor a backend restart is needed. Existing user project/version pointers are not touched.

The 9/10 target is established only after ten completed, recorded attempts and artifact verification; incomplete or fewer-run evidence must remain labelled incomplete.

## Verification precision clarification

The camera derivative’s filename rounds to 17 seconds; actual inspection reports 17.017 seconds at 30000/1001 fps. Full-source preservation therefore means 17.017 seconds in the plan and 511 output frames at 30 fps (17.0333 seconds), within one output frame. The verifier initially assumed exactly 510 output frames and stopped on the already-completed third export; this was a verifier defect, not an application retry or a changed full-source criterion. The verifier now derives encoded frame count from ceil(plan interval × 30), while separately checking the plan and encoded duration against the inspected source within the original 0.05-second tolerance. A later plan rounded the same input to 17.000 seconds and produced 510 frames, a 17ms difference. Both cases retain their original artifacts and job IDs; no verification stop caused a paid retry. This frame-scale tolerance is reported rather than described as exact audio/frame identity.
