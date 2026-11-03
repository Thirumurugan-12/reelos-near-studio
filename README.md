# ReelOS

An AI creative director for short portrait videos. Meta Muse proposes an edit; SAM tracks the subject; a validated timeline drives a deterministic compositor and FFmpeg export. Chat revisions create new versions instead of replacing earlier results. Several short clips (a trip, an event, a day out) can also become one beat-cut reel: Muse watches the clips and plans the shots, and HyperFrames renders the result in one of three styles.

**Demo:** a 2 min 58 s walkthrough of saved real outputs (see the submission). Private footage, renders and the data volume are not in this repository; a fresh clone runs the app but cannot reproduce those exact media without your own clips.

## Run with Docker Compose

Both applications live in this repository. Docker installs Python, Node, FFmpeg, HyperFrames, Remotion (fallback), Chrome Headless Shell, and the required font/runtime dependencies.

1. Copy `.env.example` to `.env` and set `MODEL_API_KEY` locally. Keep it server-side.
2. Run `docker compose up --build -d`.
3. Open [ReelOS](http://127.0.0.1:3000).

```sh
docker compose ps
docker compose logs --tail=30 backend frontend
docker compose down
```

Project state, footage, tracking masks, versions, exports, and the API ledger persist in the `reelos-data` named volume. `docker compose down` retains it. The frontend is the sole published service and binds to loopback; this release is a controlled single-user workspace, not a public multi-tenant service.

Provider keys are passed to the backend at runtime, excluded from image build contexts and Git, and never sent to the browser. The app respects `REELOS_API_BUDGET_USD` up to the $150 ceiling; the current local configuration may impose a lower limit. Each paid attempt reserves an allowance before dispatch. Reservations remain consumed even when a timeout leaves the provider outcome unknown. They are not a statement of confirmed Meta charges; reconcile with the account dashboard.

## Current workflow

1. Upload one MP4/MOV source up to five minutes and an optional reference up to 60 seconds, each up to 200 MB. Choose Full video (web default) to preserve the entire recording, or Short reel for a 15–30 second excerpt.
2. Describe the edit and subject. Creating a draft sends a compressed source proxy to Meta; reference proxies preserve their original composition. Muse Voice transcribes source speech for topic selection, without generating exact-word captions.
3. If SAM finds multiple subjects, choose the highlighted person from actual source thumbnails.
4. Inspect the storyboard or play the draft. The Effects picker adds all 45 catalog recipes plus three named looks, with animated previews, editable settings and supporting-media cards. The original subject text, spotlight, labels and Remotion inserts remain available. See the [complete catalog](docs/EFFECT_CATALOG.md).
5. Use Edit → Framing → Room for titles when a headline needs clear space. This creates a new version using existing tracking. [Recovery workflow and evidence](docs/TITLE_LAYOUT_RECOVERY.md).
6. Request changes such as “lower the headline,” “soften the spotlight,” or “make the opening faster.” The last request shortens opening effects; it does not change speech speed.
7. Compare versions, restore a prior playable edit, and export a 1080 × 1920, 30 fps H.264 MP4 with source audio.

**Multi-clip reel.** In Media → Multi-clip reel, add two or more clips (each up to 2 minutes). Choose Calm, Energetic or Clean, optionally a title, and Make reel: ReelOS converts HDR to SDR, turns very short clips into slow motion, sends one Muse Spark request with every clip attached, snaps the proposed shots to the style's beat grid and renders with HyperFrames. Times and dates come from the clips' metadata, never from the model. Change style re-times Muse's original shots and re-renders without a new Muse request. See [Multi-clip reel](docs/MULTI_CLIP_REEL.md).

Canvas Pro keeps the video and compact timeline in a fitted workspace. Edit, Looks and Media open contextual controls: a side inspector on desktop and a bottom sheet on mobile. Long forms scroll inside the controls without scrolling the page. Version history and export stay in the header. See [the Canvas Pro implementation and validation](docs/CANVAS_PRO.md).

The initial prototype used a 20-second excerpt. Full-video mode now validates source coverage from zero to the complete source duration; it rejects an excerpt instead of silently shortening the recording. The CLI selects this mode with `draft --full-length`. Originals and generated outputs are ignored by Git.

## Repository

```text
backend/                 FastAPI, durable jobs, timeline, compositor, Meta integrations, CLI
  scripts/decode-sam.mjs  Official Meta parser for fast mask decoding
  tests/                 Contract, media, API, revision, segmentation, and ledger checks
frontend/                Next.js/React workspace
graphics/                Illustration templates (HyperFrames default, Remotion fallback) and the multi-clip reel template
skills/reelos-effects/   Portable skill instructions using the shared service
docs/                    Product specifications and measured progress
demo-final/              HyperFrames source of the submission demo (private media not included)
compose.yaml             Backend + frontend deployment with health checks
```

SQLite stores project/job/version records. A single background executor runs jobs, with no additional queue service required for this initial single-user release. On restart, interrupted jobs are marked for review rather than automatically repeating paid calls. SAM responses and decoded masks are cached; changes to text placement or spotlight intensity reuse them.

## Local development

Requires Python 3.12+, uv, Node 22, npm, FFmpeg, and ffprobe.

```sh
uv --directory backend sync --frozen
npm --prefix backend ci --ignore-scripts
npm --prefix frontend ci --ignore-scripts
npm --prefix graphics ci --ignore-scripts
uv --directory backend run uvicorn reelos.api:create_app --factory --host 127.0.0.1 --port 8000
# Separate terminal:
npm --prefix frontend run dev
```

Local development uses the root `data/` directory, while Compose uses its named volume. Do not run paid work against separate copies of a budget ledger. When migrating local projects, stop the local backend first, back up both stores, copy into an empty Compose data volume, and preserve ownership for UID 10001. The initial development data and usage ledger were migrated into the current Compose instance during verification.

## CLI / skill interface

The CLI calls the same API as the browser. With Compose:

```sh
docker compose exec backend /app/backend/.venv/bin/reelos --url http://localhost:8000 health
docker compose exec backend /app/backend/.venv/bin/reelos --url http://localhost:8000 usage
```

During local development, use `uv --directory backend run reelos --help`. Commands include `create`, `upload`, `draft`, `revise`, `render`, `job --wait`, `plan`, `effects` and `apply`. Keep returned project, asset, version, and job IDs. A wait timeout does not mean a provider request failed; inspect the same job before retrying. The [skill](skills/reelos-effects/SKILL.md) documents the workflow.

## Verification

```sh
uv --directory backend run pytest -q
uv --directory backend run ruff check reelos tests
npm --prefix frontend run typecheck
npm --prefix frontend run build
npm --prefix frontend audit --omit=dev
npm --prefix graphics audit --omit=dev
docker compose config --quiet
```

Backend tests generate their own tiny videos and include a real, recorded SAM response to a generated red square. Tests do not call paid APIs. Run `npm --prefix backend ci --ignore-scripts` first so segmentation fixtures use the official native JavaScript parser.

Real model verification is documented in [the evaluation report](docs/EVALUATION.md). Three independent footage sets now have playable exports and nine exact targeted revision checks; see [results and quality limitations](docs/THREE_SET_EVALUATION.md). [Three fresh-project rehearsals](docs/REHEARSALS.md) also pass. The [complete-effects recording and extended master](docs/EFFECT_DEMO.md) are verified at 101.4 and 193.4 seconds respectively. All 45 recipes and three extra looks appear on the supplied footage. [Local delivery instructions](docs/DELIVERY.md) identify the current artifacts and remaining submission gates. Creator feedback and human listening review remain open.

## Scope and provenance

The application and original illustration code are authored here. The complete catalog adapts all 45 actual MIT-licensed drawing recipes from Vibha Ramprakash’s Claude effects repository, with copyright, fonts and model notices retained in `backend/reelos/vendor/`. The Notion recipes and video-editor agent also informed the workflow. See [how the references apply](docs/EDITOR_REFERENCE_INTEGRATION.md). SAM decoding uses Meta's official `@meta-sam/parser` package. See the dependency lockfiles, retained package notices, and [dependency/media inventory](docs/DEPENDENCIES.md) for third-party components. New drafts record a render profile using the Aileron font embedded in locked Pillow 12.3.0. Revisions retain their parent's profile; legacy versions retain the earlier host-font policy.

Exact-word captions, elaborate transitions, full timeline manipulation, social publishing, and automatic video generation are outside the baseline. Muse outputs are validated data, never shell commands. Reference observations are proposed interpretations rather than a promise to recover a video's hidden editing settings.

Graphic inserts now render through HyperFrames 0.9.4 by default (`REELOS_GRAPHICS_RENDERER=remotion` restores Remotion); the HyperFrames child runs with no credentials, telemetry or self-updates, and model text reaches it only as JSON variables. Remotion 4.0.539 renders original SVG/React graphics from four allowlisted templates: glasses, classroom, document stack, and a stylized browser mockup. Model text is passed as escaped props; the model cannot supply executable components or external asset URLs. Rendered frames are cached by template version, props, and duration. See [Remotion's licence](https://www.remotion.dev/docs/license/pricing); its free tier covers individuals and companies of up to three people, with different terms for larger organizations. This independent demo does not copy the reference's logos or screenshots. The lockfile overrides a vulnerable transitive Zod release with 4.6.7; the graphics dependency audit passes.

The [fixed ten-attempt reliability batch](docs/RELIABILITY_RESULTS.md) produced seven decodable exports and four sampled visual passes; the 9/10 target was not met. This newer evidence is separate from the earlier three successful rehearsals. Transport failures now retain redacted diagnostic categories without automatic paid retries.

[Measured source/output audio timing](docs/AUDIO_TIMING_RESULTS.md) now includes beginning/middle/end checks for the actual main v22 export, catalog sampler and fresh framed draft, plus a calibrated local checker. Human listening and visual lip-sync review remain separate gates.
