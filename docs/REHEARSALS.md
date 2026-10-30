# Three fresh-project workflow rehearsals

30 October 2026. Three consecutive fresh-project workflows completed without a failed model/render job. These are deliberately labelled **20-second excerpt** rehearsals of the short-reel path, not three full 167.9-second runs or three independent source recordings. The full-length main project remains separate and selected in its existing browser tab.

Each rehearsal created a project, uploaded the 20-second main-speaker derivative and 54-second reference, ran real SAM discovery, inspected the actual main-speaker thumbnail, selected subject 0, ran Muse Voice and Muse planning, rendered a preview, requested one precise headline-position revision, compared the entire parent/child plans, restored the baseline and exported/downloaded 1080p MP4.

SAM, speech transcription and planning were fresh per project. Subject selection resumes from the already-completed SAM artifact; the draft phase therefore reuses its own discovery masks. Deterministic Remotion illustration frames are shared when their approved props match. These are fresh-project rehearsals, not a cold-machine benchmark.

## Measurements

| Run | SAM provider seconds | Post-selection first preview, worker / observed seconds | Revision worker seconds | Export worker seconds | Export bytes |
|---|---|---|---|---|---|
| 1 | 13.50 | 43.39 / 43.49 | 14.72 | 55.28 | 15,259,937 |
| 2 | 10.80 | 38.29 / 38.44 | 13.03 | 55.20 | 15,256,936 |
| 3 | 10.52 | 34.82 / 35.44 | 14.11 | 55.66 | 15,251,016 |

Worker processing excludes queue wait. Observed values measure client dispatch to observed terminal response for that phase, including polling delay. SAM figures are the separate provider-request latency, excluding upload and decoding. No complete upload-to-preview cold-path figure was recorded; do not add these partial measurements and call the result an end-to-end benchmark.

All three exports are exactly 20.000 seconds, 1080 × 1920, 30 fps, 600 frames, H.264/AAC. Entire files decode without errors. All three actual workspace previews also reached currentTime=20, ended=true, readyState=4 in the real browser. Source/export decoded-audio correlation is 0.999203 in all three. Actual export frames at 2.5, 7.5, 11.5 and 16.5 seconds were inspected for headline, spotlight/contour, tracked label and original illustration. All three targeted revisions changed only headline y=0.10 → 0.12; both version previews remained available. Baselines were restored and retained their exports.

## Durable IDs

| Run | Project | Baseline | Revision |
|---|---|---|---|
| 1 | `59be7d7ab8204addbffb015bf3def6ad` | `4edfa0fecadd47f1b26f2f198e78158d` | `ffefe5f0863e497b8a62f9039e3af2e3` |
| 2 | `1f2f45937dac4b9f88c81abeea08ac04` | `7c7193aebf9849e098ec0f67a215e823` | `d583f88cfbfd4817ab1245c1ef498cb3` |
| 3 | `5988d17cb3a34cf2967a0b442c6d6936` | `5916fdeb69cc4e829955f91a95080d96` | `2677c275e4b34e62a643ba692006a200` |

Detailed job IDs, phase responses, observed times, output hashes and metadata remain in ignored `data/rehearsals/results.json`; discovery evidence and actual thumbnails are beside it. API budget after these runs: **$46 reserved against the configured $50 cap**, **$1.20548550 estimated from known usage**, and **two unpriced historical calls**. Reservations and estimates are not confirmed account charges; the original $150 issued credit does not override the lower configured guardrail.

## Reproduce without duplicating paid calls

1. Follow root README startup and use the running Compose backend through frontend origin `http://127.0.0.1:3000`.
2. Use the documented CLI to create a clearly labelled rehearsal project; upload the rights-cleared 20-second source and reference using absolute paths.
3. Draft with an explicit selected short-reel mode (CLI default); preserve the complete 20-second input. Request a headline, spotlight, label and a supported original illustration.
4. Retain every returned job ID. Wait on that same job; inspect real subject thumbnails before resuming with `--subject-id` if selection is required.
5. Compare the original and actual preview, request only one headline y-position change, and compare complete plans.
6. Restore the earlier playable version through the workspace and export it. Verify metadata, source audio, frame samples and full playback.
7. Never restart the backend during an active paid job or repeat an unknown paid request automatically. A new project is a new paid run; inspect `usage` before dispatch.

The rehearsals revealed a version-label defect: exporting an earlier version moved its record to the front of an update-ordered list, reversing v1/v2 display labels. The API now sorts by immutable creation time. A regression test reproduces the old failure and passes with the fix; the deployed browser shows the correct original v1 and revision v2. All 56 backend tests and Ruff passed.

These three successful rehearsals do not establish 9/10 general end-to-end reliability, creator usefulness, or time savings. Creator task feedback and the final recorded demo remain separate pending gates.
