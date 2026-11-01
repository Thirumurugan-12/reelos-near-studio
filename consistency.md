# ReelOS — complete session handoff

Updated: 1 November 2026, Asia/Kolkata. Written for continuation from another Codex account.

## Read this first

- Workspace: `/Users/thiru/Documents/ChatGPT/meta-ai-hack`.
- Git branch: `codex/reelos-foundation`.
- Latest implementation/evaluation commit before this handoff: `30cd35a`.
- Product: **ReelOS**, a Meta-powered conversational video editor for the Meta AI Developer Hackathon.
- The application and local demo videos work. **The full hackathon goal is not complete or submitted.** The previous account's goal was marked **blocked**, after repeated waits for budget authorization, human feedback/review, and participant-only portal requirements.
- User is changing Codex accounts because Codex credits are low. **Codex credits and Meta API credits are separate.** Do not infer Meta billing exhaustion from the account switch.
- Start with this document, `README.md`, `tasks/todo.md`, `docs/COMPLETION_AUDIT.md`, and `docs/DELIVERY.md`. Treat current files, live service and retained evidence as authoritative over any summary.
- Do not rebuild the project from scratch, replace the approved design, repeat paid model calls, or erase earlier failed evaluations.

## Original objective and user decisions

Build a real, demo-ready hackathon submission, initially a 15–30 second portrait edit of one talking-head source, with:

1. Upload, media inspection, validated timeline and FFmpeg export.
2. Real SAM subject tracking and text behind the speaker.
3. Real Muse analysis and structured creative planning.
4. Subject spotlight and tracked labels.
5. Conversational targeted revisions, immutable versions, comparison and restore.
6. A polished responsive editing workspace: assets, prominent preview, storyboard/chat, compact timeline, export.
7. Optional reference-video analysis mapped to supported effects.
8. Measured evaluation, provenance, setup docs and a reproducible demo.

Later explicit user instructions expanded the scope:

- Frontend and backend in the **same repository**, deployed with **Docker Compose**.
- Mobile-first, desktop-compatible. Mobile should feel like a fitted editor without document scrolling; contextual sheets may scroll internally.
- Prioritize actual editing functionality for the hackathon, then polish/check mobile.
- Use the replacement source in `testing_videos/`, not an earlier video.
- Edit the **complete two-minute-plus recording**, not just the first 19 seconds. Full-video mode now exists; Short reel remains explicit.
- Make effects visibly designed and animated, especially typography. A valid but nearly unchanged MP4 is not good enough.
- Original Remotion illustrations can provide assets absent from the source. User later preferred B-roll-style asset presentation over repeated full-screen graphics.
- Demonstrate a source-only edit without a style reference and explain the pipeline honestly.
- Implement the full Claude effects catalog. User referred to roughly 43/48 effects; inspected upstream actually has **45 recipes + 3 named looks**, all implemented here.
- Redesign UI and typography/buttons after rejecting the earlier boxy look. User approved **the first design option**, implemented as **Canvas Pro**.
- Most recent creative request: generate every effect on the supplied video and include them in the demo being recorded. **Done**, with all 48 entries, not an arbitrary 43-entry subset.
- Creator usability feedback was explicitly deferred by the user until the end. Do not fabricate it or repeatedly ask for it.
- Routine implementation is authorized. **External publication/submission is not authorized.**

## References and design history

Original sources supplied by the user:

- Shared prior chat: https://chatgpt.com/share/6adf86b5-fad8-83e8-b6be-cb9317eb53aa
- Hackathon: https://cerebralvalley.ai/events/~/e/meta-ai-developer-hackathon/details
- Claude effects: https://github.com/Vibha-Ramprakash/claude-video-effects/
- Video editing workflow: https://github.com/jeremylongshore/tons-of-skills-marketplace/blob/main/plugins/packages/creator-studio-pack/plugins/video-production/video-editor-ai/agents/video-editor.md
- Styling guide: https://feedmedia.notion.site/How-to-edit-videos-with-Claude-every-effect-from-my-video-4041d073e26281f690a6f4ab2f5f1e93
- Design inspiration sites: minimal.gallery, detail.design, navbar.gallery, cta.gallery, 404s.design, maxibestof.one, seesaw.website, a1.gallery, supahero.io.

Historical pasted files, if still present:

- `/Users/thiru/.codex/attachments/2193c843-b289-4894-94f1-a41a778aae6b/Pasted text.txt` — event-related paste.
- `/Users/thiru/.codex/attachments/d9857196-600f-4132-9839-46633b1cc1bb/Pasted text.txt` — styling/prompts.

The repository documents preserve the relevant interpretation; do not depend on shared-chat access or assume these external pages are unchanged. Current participant portal requirements remain unverified; the latest real-browser visit redirected to sign-in.

Current Canvas Pro design uses a dark/lime workspace, self-hosted Montserrat, Inter, Archivo Black and Space Mono, compact lanes, contextual inspectors and mobile bottom sheets. Desktop/mobile viewport checks cover 320–1440px with no document scrolling. See `docs/CANVAS_PRO.md`. Design option sources remain in `docs/design-proposal/options/`; prior reference captures are in `docs/design-references/`.

## Architecture and implemented capabilities

- `backend/`: Python 3.12+, FastAPI, Pydantic timeline validation, SQLite durable records/jobs and budget ledger, Meta integration, SAM decode/tracking, deterministic compositor, FFmpeg, CLI.
- `frontend/`: Next.js/React/TypeScript Canvas Pro editing workspace.
- `graphics/`: allowlisted original Remotion illustration templates and renderer.
- `skills/reelos-effects/SKILL.md`: portable skill using the same API/engine as the web application.
- `compose.yaml`: backend + frontend, health checks, persistent data volume, loopback frontend binding.
- `demo-showcase/` and `demo-master/`: editable HyperFrames presentations built from real footage/results and real UI captures.

Pipeline: upload → inspect/proxy → real SAM person discovery/selection → Muse Voice approximate speech transcript when audio exists → Muse Spark validated plan → subject-aware/graphic composition → preview/export. Revisions apply constrained changes and create child versions, preserving parent/unrelated settings. Restore selects an existing playable version.

Models recorded in real execution: `muse-spark-1.3`, `muse-voice-transcribe-1.0`, `sam-3.1`. SAM responses use Meta's official parser and source-specific cached masks. The three original effects are behind-subject text, spotlight and tracked label. Reference observations map only to supported operations; arbitrary hidden edit reconstruction is not claimed.

All 45 upstream effect recipes and 3 named looks are available through the UI, API and CLI, with animated catalog previews and project-scoped supporting media. The bridge uses actual upstream drawing functions and SAM integration. Card recipes without supplied supporting assets can use sampled source stills; these are not automatically discovered moving B-roll.

Original Remotion templates: glasses, classroom, document stack and stylized browser mockup. Model output is validated data/escaped props, never executable components or shell commands. Illustrative cards/charts are graphics, not factual screenshots/evidence.

Full-video mode covers source_in=0 through the inspected complete duration and rejects accidental excerpts. Upload limits: source ≤5 minutes/200 MB; reference ≤60 seconds/200 MB. Next proxy supports the larger upload. Export is portrait 1080×1920, 30 fps H.264, preserving source audio where present. A bounded last-picture hold preserves the brief audio tail when source video ends slightly early.

## Runtime, credentials and accounting — critical

- App URL: `http://127.0.0.1:3000`.
- Compose backend is internal on port 8000; frontend is the published loopback service.
- Credentials exist locally in `.env` as `MODEL_API_KEY`. **Never print, paste, copy into this file, commit, or expose the key to the browser.** Read variable names, not secret values.
- The user approved raising the local reservation cap from $50 to **$75**, not to $100.
- Current verified ledger: **$75.00 reserved / $75.00 local cap**, **$1.87104170 estimated known usage**, **7 unpriced calls**.
- Reservations are conservative per-attempt allowances, **not confirmed Meta charges or remaining account balance**. Overall user-stated Meta credit budget is $150; reconcile actual billing in the account.
- A new question was sent asking permission to raise the local cap to **$100** for a prepared ten-run batch, max 22 additional $1 reservations, no paid retries. **No answer has been received. Do not treat silence, automatic goal continuations, or this handoff as approval.**
- Config variable: `REELOS_API_BUDGET_USD`; allowance variable: `REELOS_REQUEST_RESERVE_USD`. Do not raise or reset the limit/ledger automatically.
- Do not start a second backend against local `data/` and spend through a separate ledger. Compose is authoritative and uses `/data` in named volume `meta-ai-hack_reelos-data` (verify actual Compose volume name).
- **Never instantiate `Editor` on the live data store during active jobs**: constructor/restart recovery can mark active jobs failed. Use read-only API queries or read-only SQLite access for audits.
- Last verified state: healthy service, **no queued/running jobs**, no paid calls made by the latest local verification/demo work. Recheck before deployment/restart.
- Unknown/timeout outcome is not permission to retry. Poll the same durable job ID, inspect state, retain conservative reservations. HTTP 402 occurred earlier, followed by key replacement and local guardrail diagnosis; HTTP 503 and an unknown transport outcome remain recorded historical failures.

## Persistent project/version identities

Do not change these current selections during unrelated evaluation:

| Purpose | Project ID | Selected version |
|---|---|---|
| Main complete source | `25ec54f2c76e4b87b9357927edf8d6a9` | v22 `7d7cc51f54a3460fb7cc8b59597490fc` |
| Complete effects catalog | `d2ce7b1de35f4b748fc4f7f85de701c6` | v1 `fefd338000bd45929b522479bad068f8` |

Main source asset: `6cf53766582d495ebfeeef1fe25107d4`; catalog clone: `b558c80d78054c2483074eb9557e2977`.

Fresh framing-permitted successes:

- Main project `b8d22a5601b84aa4b77e45827555b711`, initial version `b0283460b807454987baaa8f88001fac`.
- Camera project `b41131d06d7241a68f9772a91de223fe`, initial version `abc797239b0d470589ed2554217d519a`.

Read `docs/TITLE_LAYOUT_RECOVERY.md`, `docs/THREE_SET_EVALUATION.md` and `docs/REHEARSALS.md` for other retained evaluation/child IDs.

## Authorized media and private state

- Source: `testing_videos/VID_20261012_002734_182_bsl.mp4`, 167.900417 s container duration; original video ends at 167.8 s, audio slightly later. Source is user-authorized for processing/demo.
- Source SHA-256: `f545a15ce3be8208c9dbf27aac93bfddc8d92af972ef337619461934d0f18dc5`.
- Reference: the MP4 in `reference_video/` beginning `Claude watermarking issue Same content, no watermark.`; use directory discovery rather than guessing its punctuation.
- Main 20-second derivative: `data/demo-inputs/new-raw-20s.mp4`.
- Licensed technical sources: `data/evaluation-media/pexels-7261921-20s.mp4` (MART PRODUCTION loft), `data/evaluation-media/pexels-6617465-17s.mp4` (Anna Shvets camera, inspected 17.017 s). Both stock sources are silent; they do not test speech. Rights/source records: `docs/EVALUATION_ASSETS.md`.
- Main state/media live in the Compose named volume. Host `data/` also holds ignored exports, evidence, scripts and earlier state. **Do not substitute its database for the live volume.**
- Raw media, demo assets, `.env`, caches and output videos are intentionally Git-ignored. A new account on this machine can reuse them; **a fresh Git clone on another machine cannot reproduce the exact private demos without separately transferring authorized private dependencies and the data volume securely**.
- Preserve the live volume and ignored media. Do not run `docker compose down -v`, prune volumes, delete caches blindly, or reset the budget DB. Disk was constrained; last observed host free space was around 11 GB, so recheck before large renders. Earlier cleanup removed only unused build cache, not media/volumes.

## Current demo deliverables — ready locally

| Artifact | Path under repository root | Verified media |
|---|---|---|
| Current complete-effects recording | `data/reelos-hackathon-demo-all-effects.mp4` | 101.4 s, 1920×1080, 3,042 frames, H.264/AAC, 83,346,888 bytes |
| Extended master | `data/reelos-hackathon-master-all-effects.mp4` | 193.4 s (3:13.4), 1920×1080, 5,802 frames, H.264/AAC, 109,038,618 bytes |
| Full-size sequential catalog showcase | `data/catalog-evaluation/full-render/catalog-1080.mp4` | 167.9 s, 1080×1920, 5,037 frames, H.264/AAC, 156,173,484 bytes |

SHA-256 in table order:

```text
5a1813b0393641ba18ab6760f34cdab8edab9b0cbc1ef22760c382245ac62f5d
356d71a9aeb43342f6176681d6db07c5c2d8d1f62236e4893b9637c0ce2a44fa
6a8f4eb69e9caeb9a0ecbb589504794c901f764d0dbafe44a58d7ba665d9a99e
```

- Recording gallery: **0:20–0:58.4**, all 48 labelled entries, 12 groups of four simultaneous tiles, each group 3.2 s, normal speed.
- Master gallery: **0:55–1:33.4**. The master exceeds the PID's approximate three minutes to fit the requested full gallery. **Neither duration is a verified portal limit.**
- Tile clips: `demo-showcase/assets/effect-gallery/fx-01.mp4` through `fx-48.mp4`, also in master assets; each 432×768/30 fps/96 frames/3.2 s. Muted in the simultaneous gallery to avoid four overlapping speech tracks. Sequential sampler retains speech.
- `EFFECT_GALLERY.json` freezes intervals, labels and source/clip hashes in both projects. `ASSET_LEDGER.json` documents all private assets.
- Recording ledger has 75 assets; master has 70, including all 48 gallery entries. Actual hashes were checked; rebuild preserved all prior media bytes.
- `demo-showcase/prepare_effect_gallery.py` verifies source identity, clip geometry/frame count and exact clip hash. Same-size wrong footage is rejected. A different encoder may produce different bytes; visually review before intentionally creating new hashes.
- `demo-master/prepare_assets.py` verifies/rebuilds gallery dependencies and preserves gallery ledger entries. Both helpers make no paid calls and leave editable composition HTML alone.
- HyperFrames version pinned to **0.8.220**. Full composition checks and encoded group frames passed. Recording: 31/31 contrast checks; master: 24/24. Intentional scene-local nested media timing warnings were inspected, not blindly shifted to global times.
- Full-file decoding passed for both final demo exports. All 12 encoded gallery groups were inspected. Background music is presentation music from the existing original instrumental, not a claimed ReelOS music-sync feature. Human listening remains unverified.
- The composed demos show saved outputs and actual interface captures, not fake live generation or fabricated latency.
- Historical 75-second files remain: `data/reelos-hackathon-demo.mp4` and `data/reelos-hackathon-demo-canvas-pro.mp4`.
- Editable preview addresses: `http://127.0.0.1:3017/#project/demo-showcase` and `http://127.0.0.1:3020/#project/demo-master`. Confirm managed preview status; ports/tab IDs from the old account are not guaranteed in a new session.

## Verified results and honest limitations

1. **Real Meta execution** is retained in the live ledger/jobs. Never replace it with mocked results.
2. **Three rights-cleared footage sets** have real playable exports. Ten encoded frames per stock set and actual browser playthrough were checked. The camera case's hard spotlight silhouette remains a visible quality limitation.
3. **Nine targeted Muse revision trials** changed exactly the intended field across complete plan comparisons. Three fresh-project rehearsals passed. These are limited measured results, not general reliability guarantees.
4. **Original fixed ten-attempt cohort failed the 9/10 target**: 7 pipeline exports, **4 sampled visual passes**. Preserve all ten attempts, HTTP 503/unknown failures and occluded-title outcomes. Do not replace failures or combine different cohorts into a passing score.
5. **Explicit framing recovery** now exists in Edit → Framing → Room for titles / Original framing, shared API and CLI. Room for titles uses scale .82 / vertical offset .16 and transforms SAM masks with footage. New immutable child, no model call. Two recovered exports verified; this does not retroactively pass failed initial drafts.
6. **Two separate fresh framing-permitted drafts** passed real Muse/SAM, readable designed/animated titles, native preview playthrough and 1080p export **without manual layout repair**. This is only two-case feasibility, not 9/10 reliability.
7. **Moving-title validation fix**: original renderer checked visibility only at midpoint. Saved camera titles had about 44% visible there but 33% later. It now checks quarter/midpoint/three-quarter positions against the existing 40% threshold. All three bad camera replays reject; three readable real-footage layouts render/decode. Three samples/alpha area do not prove universal semantic readability or flicker-free masks.
8. **Audio alignment**: actual selected v22, catalog sampler and fresh framed main draft passed beginning/middle/end comparison, nine windows total: 0 ms measured lag at 24 kHz, correlations >.998. Historical full export passes three additional windows. This is decoded audio alignment, **not human listening or visual lip-sync proof**.
9. Latest full backend suite: **177 passed, 1 dependency deprecation warning**, plus Ruff. Four frontend regression tests existed at the earlier UI recovery verification; production build/typecheck and real browser checks passed then. Do not claim frontend was freshly rebuilt during the latest offline audio-only work.
10. Latest backend runtime change (three-point visibility guard) was built/deployed and health-verified with no active jobs interrupted. Later commits add local verification helpers/docs/tests; no product UI/runtime edit or paid request was needed for those.

Known unsupported/reduced claims: exact-word captions/alignment, arbitrary generative video, automatic music/beat sync, silence/filler removal, unrestricted reference reconstruction, full nonlinear timeline editing, public multi-tenant hosting, proven creator time savings. Keep supporting graphics distinct from factual evidence. Stock subjects are not customers/endorsers.

## Remaining work — do not mark goal complete

- **Budget decision:** pending request to raise the local reservation cap to $100. No answer recorded. Current cap is fully allocated; do not spend or reset it.
- A new fixed ten-run evaluation is preregistered in `docs/RELIABILITY_FOLLOWUP_PROTOCOL.md`, **not started**. Order main/loft/camera/loft/camera/main/loft/camera/loft/camera; fresh projects/assets/SAM/Muse, framing allowed, fixed copy/three effects, no repair/replacement/paid retries. Max 22 additional reservations. Follow that document exactly if allowance is approved. Keep old scores separate.
- Creator usefulness target: 2 of 3 creators; active-time savings target ≥50%; both unmeasured. User deferred this until the end. Do not invent participants or observations.
- Human listening, visual lip-sync/presentation review are still open.
- Official portal: verify deadline, video/file limits, track/team eligibility, original-work declaration, repository visibility and hosted/local access requirements through participant access. Last visit redirected to sign-in. Do not infer current rules from the old paste or the PID's proposed Nov 4 schedule.
- Adapt the submission cut only after verifying official duration requirements.
- External publication/submission requires explicit user authorization after concrete review. No GitHub PR, public demo hosting or hackathon submission has been performed as part of this final handoff work.

## Commands and operational continuation

From repository root, inspect before changing anything:

```sh
git status --short
git log -8 --oneline
docker compose ps
curl -fsS http://127.0.0.1:3000/api/health
curl -fsS http://127.0.0.1:3000/api/usage
```

API project responses are flat objects containing `current_version_id`, `versions`, etc.; don't assume a nested `project` key. Read actual response shapes.

Normal setup: copy `.env.example` to `.env` **only on a genuinely new machine**, configure secrets locally, then `docker compose up --build -d`. On this existing machine preserve `.env` and the volume. `docker compose down` retains the volume; `down -v` does not.

Checks (no paid calls):

```sh
uv --directory backend run pytest -q
uv --directory backend run ruff check reelos tests scripts/check_audio_timing.py
npm --prefix frontend test
npm --prefix frontend run typecheck
npm --prefix frontend run build
docker compose config --quiet
```

Read README for Python/Node/FFmpeg/native parser setup on a fresh checkout. Use existing lockfiles. Do not add model smoke calls simply to demonstrate that credentials still exist.

Shared CLI example:

```sh
docker compose exec backend /app/backend/.venv/bin/reelos --url http://localhost:8000 health
docker compose exec backend /app/backend/.venv/bin/reelos --url http://localhost:8000 usage
```

CLI also supports create/upload/draft/revise/render/job/plan/effects/apply/frame. `job --wait` polls an existing job; it does not redispatch. See the local skill for exact arguments and subject selection.

Presentation rebuilding (private assets required):

```sh
python3 demo-showcase/prepare_effect_gallery.py
python3 demo-master/prepare_assets.py
```

For preview/render, follow each presentation README. Use managed `hyperframes preview --background`, check status, run full composition checks and inspect actual frames after composition edits. Before editing existing HyperFrames projects, read their AGENTS.md and use history/catch-up as applicable; preserve user edits. Do not publish.

Offline audio checker: `backend/scripts/check_audio_timing.py`; examples in `docs/AUDIO_TIMING_RESULTS.md`. Current v22 audio-check export copy: `data/audio-timing/current-main-v22.mp4`, SHA-256 `daeb07559492114f86ccba9c439a062c2eceda39f93803410e53a32a294a1146`.

## Documentation/evidence map

- Product baseline: `docs/REELOS_PID.md`, `docs/CREATIVE_EDITING_SPEC.md`, `docs/DESIGN_DIRECTION.md`.
- Completion and tasks: `docs/COMPLETION_AUDIT.md`, `tasks/todo.md`.
- Current handoff: `docs/DELIVERY.md`, `docs/SUBMISSION_DRAFT.md`.
- Demo: `docs/EFFECT_DEMO.md`, `docs/DEMO_ARTIFACT.md`, both presentation READMEs/SPEC/STORYBOARD/REVIEW/ASSET_LEDGER/EFFECT_GALLERY files.
- Catalog/provenance: `docs/EFFECT_CATALOG.md`, `docs/DEPENDENCIES.md`, `docs/EDITOR_REFERENCE_INTEGRATION.md`, vendor notices.
- Baseline/reference/full output: `docs/EVALUATION.md`, `docs/REFERENCE_STYLE_IMPLEMENTATION.md`, `docs/FULL_VIDEO_VERIFICATION.md`, `docs/NO_REFERENCE_EDIT.md`, `docs/BROLL_OVERLAYS.md`, `docs/ANIMATED_TYPOGRAPHY.md`.
- UI: `docs/CANVAS_PRO.md`; obey `frontend/AGENTS.md` before frontend edits.
- Quality: `docs/THREE_SET_EVALUATION.md`, `docs/REHEARSALS.md`, `docs/RELIABILITY_PROTOCOL.md`, `docs/RELIABILITY_RESULTS.md`, `docs/TITLE_LAYOUT_RECOVERY.md`, `docs/TITLE_VISIBILITY_CHECK.md`, `docs/LAYOUT_FOLLOWUP_PROTOCOL.md`, `docs/LAYOUT_FOLLOWUP_RESULTS.md`, `docs/RELIABILITY_FOLLOWUP_PROTOCOL.md`, `docs/AUDIO_TIMING_RESULTS.md`.
- Ignored evidence folders: `data/completion-audit/`, `data/reliability/`, `data/title-layout-recovery/`, `data/layout-followup/`, `data/effect-gallery-final/`, `data/master-final/`, `data/audio-timing/`.
- Earlier reports retain dated checkpoints (e.g. 160/169/171 tests, $51/$70 reservations, historical 75-second demo). Use the latest explicit follow-ups and live state; do not silently overwrite historical measurements or confuse them with current totals.

## Reuse and licences

The complete recipe catalog adapts Vibha Ramprakash's MIT-licensed code pinned at `99c9a3393ee14d39bea155a05c73dc069f02f16f`. Notices, fonts and YuNet model licence remain under `backend/reelos/vendor/`. Upstream MediaPipe/private hooks/arbitrary file-loading behavior were excluded from the ReelOS bridge. Read `docs/DEPENDENCIES.md` and retained licences before distribution. Original application/planning/SAM integration/Remotion templates were implemented here. Remotion licensing depends on organization size; do not assume unlimited rights for a different team. Private user media is not automatically licensed for broad publication.

## Recent commits useful for orientation

- `2d958db` — Canvas Pro approved UI implementation.
- `ec4bf69`, `eed165e`, `2c3f4e5` — shared framing API/CLI/UI recovery and docs.
- `87fb039`, `9c8db9a` — preregistered two-case layout test and real successes.
- `07b87a0` — complete effects gallery and extended demo master.
- `a811ba8`, `6fb0e4b` — three-point visibility guard and deployment evidence.
- `a4b2d77` — gallery identity verification and provenance-preserving rebuild.
- `505b652` — current delivery documents and bounded next reliability protocol.
- `30cd35a` — calibrated audio timing checker and measured results.

## Starter prompt for the new account

> Continue ReelOS in `/Users/thiru/Documents/ChatGPT/meta-ai-hack`. Read `consistency.md`, README, tasks/todo.md, docs/COMPLETION_AUDIT.md and docs/DELIVERY.md first, then verify current Git/runtime state. Preserve the approved Canvas Pro design, main v22 and catalog v1, ignored media and the Compose ledger. The project works locally and has real Muse/SAM evidence, 177 passing backend tests, all 45 recipes + 3 looks, and verified demo files. The overall goal remains incomplete. Do not make paid calls or raise the fully reserved $75 cap without my answer to the pending $100 allowance question. Keep the original failed ten-run score intact. Continue the prepared evaluation only if authorized, then finish actual creator/listening feedback and current portal requirements. Do not publish or submit without my authorization. Never expose credentials.
