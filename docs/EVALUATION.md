# ReelOS implementation and evaluation

Updated 30 October 2026. This is measured progress, not a declaration that the full hackathon goal is complete.

The initial short-clip results below are historical. The user-requested complete recording is documented separately in [complete-recording verification](FULL_VIDEO_VERIFICATION.md).

## Verified

| Requirement | Evidence |
|---|---|
| One repository | `backend/` and `frontend/` with independent locked dependencies |
| Real Muse access | `muse-spark-1.3` completed the smoke request and generated editing/revision data |
| Real SAM access | `sam-3.1` segmented a generated image and processed the supplied video's frames |
| Real updated footage | A 20-second derivative from seconds 10–30 of the user's updated raw video; source preserved |
| Three effects | Real preview includes behind-subject title, spotlight, and tracked label |
| Source audio | Export retains AAC audio; decoded waveform correlation with the tested source interval was 0.99918 |
| Revision precision | Requested headline y 0.23 → 0.32 and spotlight intensity 0.45 → 0.25; exact whole-plan comparison confirmed no other changes |
| Version preservation | Initial and revised versions retained their own plans and playable previews |
| Final MP4 | 18 seconds, 1080 × 1920, 30 fps, H.264/AAC; download returned HTTP 200 |
| Background work | API test uploads actual generated media, creates a timeline, waits for its job, and retrieves the rendered MP4 |
| Budget ledger | Every paid attempt reserved an allowance before dispatch; usage and latency persisted, including unknown failures |
| Compose | Both images built; backend and frontend became healthy; existing projects and ledger were migrated into the named volume |

## Timing observations

- First generated-image SAM smoke: approximately 1.93 seconds.
- SAM processing of the updated 200-frame proxy: approximately 11.53 seconds, excluding local decoding.
- Muse planning plus preview rendering with cached masks: 16.01 seconds.
- Targeted Muse revision plus preview: 7.18 seconds.
- 1080p export of the revised edit: 16.47 seconds.

These are individual development runs on the current machine, not latency percentiles or service guarantees. The first video attempt revealed slow local mask decoding. On the same representative 360 × 640 mask fixture, the Python parser path took 0.879 seconds and the official JavaScript parser path took 0.050 seconds including subprocess startup, about 17.5× faster. The mask geometry fixture still passes after the change. This is a single-fixture benchmark; full-workload statistics remain to be collected.

## Current automated checks

56 backend tests now pass. They cover invalid plans, time mapping, missing assets, actual media decode/export, audio presence, foreground occlusion, required tracking, revision isolation, geometry decoding, durable budget claims, project scoping, cross-origin rejection, and a real API background render. Additional checks cover matched footage/mask framing, hidden-title detection, smoothed tracking anchors without filling absent masks, font independence from host fonts, and single-line short headlines at both preview and export sizes. Ruff also passes.

## Visible-edit correction

The user correctly reported that the first treatment was too subtle: the title was mostly occluded and the spotlight was weak. A new Muse-directed 18-second draft (`c8d845c855964067b03c152bd2f7bce1`) uses 0.82 framing scale, 0.16 vertical offset, a readable YOUR STORY headline at 0–6 seconds, spotlight intensity 0.6 at 6–12 seconds, and a contrasting YOUR VOICE label at 12–18 seconds. Preview frames at seconds 2, 8, and 14 were visually inspected. Planning plus preview took 15.73 seconds with cached SAM masks. These labels are editorial titles, not transcribed speech. Export inspection caught a resolution-dependent title wrap; a short-title fitting correction was applied and the same Muse plan was preserved as child version `5bc1e98a11c742c591dbde42e842cb3e`, without another paid model request. The first corrected export took 38.73 seconds; decoded source/export audio correlation was 0.99919.

An earlier correction attempt exhausted the provider's output-token limit and produced no version. The planner now explicitly uses low reasoning effort so reasoning does not consume the entire response budget. The successful subsequent request was manually initiated; failed paid requests are not automatically retried. The renderer now rejects a title with less than 40% unoccluded glyph area at its midpoint; this is a limited guardrail, not a substitute for playback review.

Frontend type checking and production build passed. The npm production dependency audit reported no vulnerabilities at that checkpoint. These do not replace browser interaction and visual checks.

## Browser checkpoint

The deployed Compose build was checked at 320 × 568, 390 × 844, 768 × 1024, and 1024 × 768: document dimensions equaled the viewport and the video was loaded (`readyState=4`). At 1440 × 900, the three-column desktop layout rendered with a 1440 × 1416 scrollable document. The fitted body requirement applies to mobile; long forms remain internally scrollable. Original/Edit switched between the verified source and rendered preview URLs. Full edited playback reached 19.5 seconds. These browser checks do not establish compatibility with every device or browser.

### Functional workspace verification, 29 October

Visual SAM selection now shows real mask-highlighted source thumbnails, including small background photo detections. The speaker was selected in the browser and a new Muse draft rendered in 14.0 seconds using cached masks. Three subsequent browser-submitted revisions changed headline y 0.09 → 0.11, spotlight intensity 0.6 → 0.35, and headline end 6 → 4 seconds. Whole-plan comparisons proved that each changed only its requested field. Preview latencies were 8.00, 8.24, and 8.85 seconds. Restoring the earlier draft through the browser changed the durable current-version pointer and retained all eight playable versions present at that checkpoint.

A controlled coral reference derived from our own renderer exercised the real reference-upload/analysis path. Muse approximated its headline as #E78A66 (the fixture used #D97757), with timestamped reference observations. The rendered reference-mapped title was visually inspected. This proves limited supported mapping on a controlled fixture; it does not prove general style matching. The user subsequently supplied a separate 54-second landscape reference, whose more elaborate treatment requires further implementation and verification.

The usage endpoint now separates known-usage cost estimates, unpriced calls, and conservative reservations. At the 15-request checkpoint it reported $0.21033950 for known usage, one unpriced request, and $15 reserved against the configured $50 cap. These are local calculations using [Meta's published rates](https://dev.meta.ai/docs/pricing-rate-limits), checked 29 October; neither is confirmed account billing. Forty backend tests passed after these additions.

## Still required

- Three-set functional evidence is now recorded in [the independent-footage evaluation](THREE_SET_EVALUATION.md); broader robustness remains unproven.
- Broaden reference matching beyond the one guided red/black adaptation documented below.
- Broaden validation of visual subject selection, label smoothing, and recorded font profiles.
- Nine targeted revision trials now pass across three independent sets; see the exact scope and timing caveats in the three-set report.
- Broaden compositing inspection across motion, occlusion, missing subjects, and effect boundaries.
- Three fresh-project workflow rehearsals now pass; see [scope and cache/timing details](REHEARSALS.md). Creator task feedback remains pending; no time-savings or preference claim is established.
- A [verified 75-second local demo MP4](DEMO_ARTIFACT.md) and submission description draft now exist. Verify current official portal rules/access, collect creator feedback and complete human presentation review before external submission.

Private raw responses, masks, footage, exports, and run metadata stay in local/Compose data storage, outside Git. API reservations are local guardrails, not confirmed account billing.

## Supplied reference and Remotion verification, 30 October

The user-supplied 54-second landscape reference now drives a guided red/black adaptation with a SAM contour, behind-person red titles, and original Remotion glasses/classroom illustrations matched to the source topic. [Implementation, provenance, timings and output evidence](REFERENCE_STYLE_IMPLEMENTATION.md). Muse Voice supplied the approximate source transcript; exact-word captions remain deferred. Preview took 40.98 seconds and 1080p export took 64.39 seconds. Both were rendered through the shared web/CLI engine.

A real Muse revision changed only the glasses-insert title to “I wanted glasses”; all other plan fields were preserved, including template, body, accent, timings and subject treatment. Its preview took 24.3 seconds. The classroom sequence was reused: two initial graphic sequences plus one changed sequence existed afterward. The original exported version was restored through the workspace.

The final QA child (`6f45a4247574489bbcac3d432681e93f`) starts the classroom illustration at 14.5 seconds and holds it to the 19.5-second output end. This covers a source-camera edge crop during the speaker’s movement and removes the short return to the speaker at the ending. The timing adjustment was manual and preserved the model-directed content and other settings.
