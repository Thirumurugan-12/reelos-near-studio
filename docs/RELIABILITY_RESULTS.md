# Ten-attempt reliability results — 1 November 2026

**The 9/10 target was not met.** The fixed protocol produced seven downloadable, fully decodable exports; four of ten attempts also passed the sampled visual acceptance check. No failed attempt was replaced or retried into the score. Read [the registered protocol and frame-precision clarification](RELIABILITY_PROTOCOL.md).

| Run | Input | Pipeline/export | Overall with visual review | Result |
|---|---|---|---|---|
| 1 | main | Fail | Fail | The headline is mostly hidden by the subject. Move it into clear space or use a framed layout. |
| 2 | loft | Pass | Pass | Readable headline and label; spotlight and late frame inspected |
| 3 | camera | Pass | Fail | Headline is largely occluded by the actual selected foreground person |
| 4 | loft | Pass | Pass | Readable headline and label; spotlight and late frame inspected |
| 5 | camera | Fail | Fail | This operation could not finish. Your previous edit is preserved. |
| 6 | main | Fail | Fail | Meta request failed (HTTP 503, service_overloaded): The backend is temporarily overloaded. Please retry. |
| 7 | loft | Pass | Pass | Readable headline and label; spotlight and late frame inspected |
| 8 | camera | Pass | Fail | Headline is largely occluded by the actual selected foreground person |
| 9 | loft | Pass | Pass | Readable headline and label; spotlight and late frame inspected |
| 10 | camera | Pass | Fail | Headline is largely occluded by the actual selected foreground person |

## What was verified

Ten fresh projects and uploaded source assets used two authorized main-speaker derivatives, four licensed loft derivatives and four licensed camera derivatives. SAM and Muse were fresh per asset. Multiple-subject thumbnails were inspected before continuing with the actual intended person; reused SAM artifacts belonged to that same attempt. No cross-project cached masks, previous plan or transcript was copied.

All seven returned exports have successful HTTP downloads, complete FFmpeg decoding, H.264 1080×1920 video at 30 fps, the three requested subject effects and durations within the registered tolerance. Four sampled frames from every export were inspected (headline, spotlight, label, late source frame). The camera's 17.017-second source produced 511 frames in run 3 and rounded 17.000-second / 510-frame plans in runs 8 and 10. This frame-scale timing variation is disclosed; do not claim exact frame identity. All seven successful new exports are silent because both audio-bearing main attempts failed. Audio preservation remains supported by the earlier main/rehearsal evidence, not independently reproved in this batch.

The four loft runs passed the sampled visual check. In three camera exports, the correct foreground person mask obscures much of the required STOCK FOOTAGE title. Those are render completions but **visual failures**. The harsh silhouette remains a known limitation. Four still samples per export do not establish flicker-free playback or broad segmentation quality.

Main run 1 was rejected by existing title-visibility validation after real planning; the fixed instruction requested a high title while forbidding framing changes. It remains a failure, not an excluded unsupported case. Run 5 has a failed/unknown SAM call with no cached response/error body; its exact cause is unproven. Run 6 has a retained, redacted HTTP 503 service_overloaded provider error. These three failures have not been repeated or refunded in the local reservation ledger.

## Diagnostic improvement

The generic run-5 failure exposed missing transport diagnostics. The Responses client now records fixed redacted categories for request timeouts, transport errors and unreadable JSON. It retains conservative reservations, reports unknown outcomes without raw exception bodies and does not retry. Four regression cases were reproduced failing first, then passed after the change; the full backend suite passes **164 tests**, plus Ruff. This helps diagnose future failures; it does not establish the historical run-5 cause or turn any failed attempt into a pass. The backend image was built separately and deployed only after all jobs were terminal.

## Budget and scope

Ledger after this batch: **$70 reserved against the approved $75 cap**, **$1.75387155 estimated known usage**, **seven unpriced historical calls**. The batch consumed 19 reservations, fewer than its 22-call ceiling because failed attempts stopped early. These are local estimates/allowances, not confirmed Meta billing. No cap increase or external submission occurred.

Private IDs, returned jobs, request markers, output hashes, source-selection notes, metadata and frames remain under ignored `data/reliability/`. This test has only three underlying recordings with repeats, explicit effect timings, no reference video and eight silent attempts. It does not establish independent creator usefulness, broad visual quality, autonomous edit selection or a cold upload-to-preview percentile. Worker times in retained jobs exclude queue/selection wait; resumed client polling times are not used as latency benchmarks.

Existing main v22 and earlier successful three-set evidence are preserved. Those earlier successes do not erase this failed reliability target. Next work should address title-layout feasibility before a new preregistered quality/reliability run; do not spend the remaining allowance on repeated attempts merely to obtain a passing score.

## Recovery follow-up

An explicit [title-headroom operation](TITLE_LAYOUT_RECOVERY.md) now recovers the failed main layout and an occluded camera title using cached tracking, without new model calls. Both 1080p child exports are verified and only framing changes. These are manual recovery demonstrations; all ten original outcomes and the four-of-ten visual score remain unchanged.
