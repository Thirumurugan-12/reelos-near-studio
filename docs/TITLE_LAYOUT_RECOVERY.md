# Title-layout recovery — 1 November 2026

The Edit inspector now exposes **Room for titles** and **Original framing**. Room for titles uses the existing framing contract (scale 0.82, vertical offset 0.16), moving the footage and SAM masks together. Original framing uses scale 1 and offset 0. Each action creates a new child version and queues the shared preview renderer. Parent plans, copy, effect timing, source interval, tracking and render profile remain preserved. This is an explicit layout change, not automatic rewriting of a creator’s fixed layout instructions.

A first failed render with a saved plan now reopens that plan after reload when no playable current version exists. If there is already a current version, it remains selected. Failed or unknown version IDs are not invented. This exposes the recovery controls without requiring knowledge of the history dialog.

## Shared interface

`POST /api/projects/PROJECT/versions/VERSION/framing` accepts the validated Framing object and returns a queued render job (HTTP 202) plus its child version ID. Invalid geometry, cross-project parents and active jobs are rejected before creating a child. The child becomes current only when rendering completes.

Web: open Edit → Framing → Room for titles. The active choice is marked and disabled; all framing controls disable during work. To recover an existing failed version manually, it is also available through Version history. Earlier versions remain available there.

CLI/skill workflow, against the same service:

```sh
uv --directory backend run reelos frame PROJECT_ID VERSION_ID --scale 0.82 --offset-y 0.16
uv --directory backend run reelos job PROJECT_ID RETURNED_JOB_ID --wait
uv --directory backend run reelos render PROJECT_ID CHILD_VERSION_ID --quality export
```

No model call is made by framing/rendering; existing source-specific SAM masks are reused. A new draft or conversational model revision still has its normal budget behavior. A preset cannot guarantee legibility for arbitrary title positions, sizes, motion or copy; inspect the actual output. Returning to an unreadable original framing can still be rejected by the existing renderer’s visibility check.

## Actual recovery evidence

| Case | Parent → separate recovery child | Verified artifact |
|---|---|---|
| Failed main short input | `153a8b74d7f64b0e89ab695487cc9521` → `af15a7f3bbb0466a82c82ddedfd92d02` | 20.000 s, 600 frames, 1080×1920 H.264/AAC, 17,813,113 bytes |
| Occluded camera short input | `5a1851020345443597bfdfeec655e96d` → `8c92f63f008748dfa9b41bb74abb995e` | 17.0333 s, 511 frames, 1080×1920 H.264, silent source, 4,509,008 bytes |

The main child was created by the real web control; the camera child by the real CLI. Both use the same endpoint and rendering engine. Whole-plan comparisons prove only framing changed, with tracking and parent profile retained. Both complete exports decode without errors. Actual encoded frames at 2, 6, 11 and 16 seconds were inspected. MY STORY and STOCK FOOTAGE are readable; spotlight, contextual labels and late source frames remain present. The camera’s hard mask edge is still a known visual limitation. Main source/export decoded audio correlation at zero lag is 0.99911547; no exact sample-identity or listening claim is made.

The real browser shows the recovered main preview at readyState 4 and 20 seconds. Desktop control/preview and 390×844 mobile sheet were checked: document equals viewport, both framing targets are 44px tall, and active states reflect the actual plan. Four frontend tests include recovery selection and preservation of a playable current version. Backend API/CLI regressions plus the full 167-test suite and Ruff pass. Docker production builds and deployment passed; no active jobs were interrupted.

Private exports, returned jobs, hashes, comparisons, inspection sheets and browser evidence live under ignored `data/title-layout-recovery/`. No new paid calls were used: reservations remain $70/$75, known estimate $1.75387155 and seven unpriced historical calls. Existing main-project v22 and full catalog demo v1 remain current. The original ten-attempt cohort still has seven pipeline exports and four visual passes; these manually repaired children do not change that score.
