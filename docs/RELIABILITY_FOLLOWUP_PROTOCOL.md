# Framing-permitted ten-attempt follow-up protocol

Prepared 1 November 2026 before dispatch. **Not started: additional local reservation allowance is required.** The original ten-attempt result remains seven pipeline exports and four visual passes. The two-case framing feasibility check is separate. This new batch measures the current renderer with framing explicitly permitted; it is not a controlled experiment isolating the visibility-validator change.

## Frozen sample

Order: main, loft, camera, loft, camera, main, loft, camera, loft, camera. Use the same three rights-cleared recordings and derivatives as the original cohort; this is ten attempts over three underlying recordings, not ten independent video sources. Each attempt gets a fresh project/upload and fresh SAM/Muse calls. Do not copy another attempt's tracking, speech or plans. Reuse only that attempt's discovery masks after normal subject selection.

| Input | Local file | Inspected duration | SHA-256 |
|---|---|---:|---|
| Main speaker, with speech | `data/demo-inputs/new-raw-20s.mp4` | 20.000 s | `49584d7653727dbfc761508ec6ac81ce25af8a77784ec97836544b94dbb01d65` |
| Silent loft | `data/evaluation-media/pexels-7261921-20s.mp4` | 20.000 s | `9340114ca400521364978cd6e2b72579c41f86df112226a8cd8821785c34963c` |
| Silent camera/occlusion | `data/evaluation-media/pexels-6617465-17s.mp4` | 17.017 s | `4086273f67b9c65c68c703c8251a85214937da53f7d10fc959907fda5fb347e9` |

Source permission/licences remain in EVALUATION_ASSETS.md. Verify the hashes before starting. Record the deployed commit, container image, model IDs, runtime versions, cache state and initial/final usage ledger. Require at least 5 GB host free space and 2 GB inside the data filesystem before each new attempt; a resource stop leaves the batch incomplete.

## Fixed direction

Use output_mode full, subject prompt person, no reference, and the exact inspected source duration. Substitute only duration and copy below; do not tune prompts between attempts:

> Create a portrait technical evaluation of the complete {duration}-second derivative, source_in=0 and source_out={duration}, preserving source audio and timing. Use exactly three effects: behind_subject_text id headline from 0 to 4, text {title}; subject_spotlight id focus from 4 to 8 intensity .3 with the original background; tracked_label id tag from 9 to 13, text {label}. You may choose framing, headline/label placement, size and design to keep the text readable. Framing may create headroom, for example scale .82 and offset_y .16. Preserve subject identity and keep graphics within the frame. No other effects, transcript captions, music or invented speech. This is a labelled short input derivative, not a claim that the complete original recording is edited.

Main copy: MY STORY / PERSONAL STORY. Stock copy: STOCK FOOTAGE / TECHNICAL TEST. Selecting the intended person after inspecting actual SAM thumbnails is normal workflow. Log selection wait separately. No manual plan/framing repair, regeneration or paid revision is allowed inside this first-draft batch. Repaired examples, if later requested, must remain separate.

## Acceptance and retention

Retain all ten fixed slots and failures. Provider/validation/render failures count; never substitute an extra success. A pass requires upload/inspection, real fresh SAM and Muse execution, playable native preview, a downloaded 1080×1920 / 30 fps H.264 export, three supported effects and a complete error-free decode. Preserve the inspected source interval and audio presence. Allow at most one output-frame rounding difference, with frame count consistent with the saved plan and engine; record actual values rather than claiming exact identity.

Inspect encoded frames at headline 0.5/1/2/3 seconds, spotlight 4.2/6/7.8, label 9.5/11 and a late frame (16 seconds for camera, 19 for others). Review actual selected-person continuity, readable headline/label, spotlight visibility and major mask errors. Play every preview through in the browser and retain ended/readyState/media-error evidence. For the two speech-bearing outputs, compare source/output audio at beginning, middle and end and retain correlation/lag results; human listening remains a separate unverified gate. A decodable file with an unreadable title fails the visual score.

Report pipeline completions and visual passes separately, with all failure reasons and artifacts. Worker timings exclude selection/queue wait and do not establish a cold start percentile. Ten samples per export and browser playback do not prove universal flicker-free segmentation. Report the known camera silhouette limitation explicitly. The proposed 9/10 target requires at least nine complete and visually accepted attempts; incomplete evidence cannot pass.

## Budget and dispatch policy

Initial local ledger: $75 reserved, $1.87104170 estimated known usage and seven unpriced calls. The approved local cap is $75, so **no paid dispatch may begin under the current allowance**. A proposed increase to $100 remains within the user's $150 outer budget; it requires a new user decision, not an automatic change.

Maximum batch allowance: 10 SAM + 10 Muse + 2 speech calls = 22 additional $1 reservations, at most $97 total. This is an allowance, not a predicted Meta charge. Stop on an unexpected extra paid call requirement; do not consume the remaining $3 as implicit retry permission. No paid retry after failed/unknown outcomes. Poll the same durable job; observation timeouts are not failures or permission to redispatch. Inspect durable state when a dispatch result is ambiguous. Pause new dispatches if provider access/billing fails. Do not raise any limit beyond the separately approved amount.

Private job/request markers, selected thumbnails, plans, outputs, sample frames and measurements belong under ignored `data/reliability-followup/`. No existing main/catalog pointer may change. This protocol does not authorize publication or submission.
