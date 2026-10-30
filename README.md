# ReelOS

An AI creative director for short portrait videos. Meta Muse proposes an edit; SAM tracks the subject; a validated timeline drives a deterministic compositor and FFmpeg export. Chat revisions create new versions instead of replacing earlier results.

## Run with Docker Compose

Both applications live in this repository. Docker installs Python, Node, FFmpeg, Remotion, Chrome Headless Shell, and the required font/runtime dependencies.

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
4. Inspect the storyboard or play the draft. Effects include text behind the subject, spotlight with optional black/monochrome background and glowing outline, tracked labels, and original Remotion illustration cutaways when requested.
5. Request changes such as “lower the headline,” “soften the spotlight,” or “make the opening faster.” The last request shortens opening effects; it does not change speech speed.
6. Compare versions, restore a prior playable edit, and export a 1080 × 1920, 30 fps H.264 MP4 with source audio.

Mobile uses a fitted workspace with Preview, Assets, Direction, and Storyboard tabs. Long forms scroll within their panels. Desktop displays assets, preview/timeline, and direction together.

The initial prototype used a 20-second excerpt. Full-video mode now validates source coverage from zero to the complete source duration; it rejects an excerpt instead of silently shortening the recording. The CLI selects this mode with `draft --full-length`. Originals and generated outputs are ignored by Git.

## Repository

```text
backend/                 FastAPI, durable jobs, timeline, compositor, Meta integrations, CLI
  scripts/decode-sam.mjs  Official Meta parser for fast mask decoding
  tests/                 Contract, media, API, revision, segmentation, and ledger checks
frontend/                Next.js/React workspace
graphics/                Approved, parameterized Remotion illustration templates and renderer
skills/reelos-effects/   Portable skill instructions using the shared service
docs/                    Product specifications and measured progress
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

During local development, use `uv --directory backend run reelos --help`. Commands include `create`, `upload`, `draft`, `revise`, `render`, `job --wait`, and `plan`. Keep returned project, asset, version, and job IDs. A wait timeout does not mean a provider request failed; inspect the same job before retrying. The [skill](skills/reelos-effects/SKILL.md) documents the workflow.

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

Real model verification is documented in [the evaluation report](docs/EVALUATION.md). Three independent footage sets now have playable exports and nine exact targeted revision checks; see [results and quality limitations](docs/THREE_SET_EVALUATION.md). [Three fresh-project rehearsals](docs/REHEARSALS.md) also pass. Creator feedback, the final demo recording and current portal checks remain open.

## Scope and provenance

The implementation is original project code. The supplied Claude effects repository, Notion recipes, and video-editor agent informed the workflow and catalog; their renderer code was not copied. See [how the references apply](docs/EDITOR_REFERENCE_INTEGRATION.md). SAM decoding uses Meta's official `@meta-sam/parser` package. See the dependency lockfiles, retained package notices, and [dependency/media inventory](docs/DEPENDENCIES.md) for third-party components. New drafts record a render profile using the Aileron font embedded in locked Pillow 12.3.0. Revisions retain their parent's profile; legacy versions retain the earlier host-font policy.

Exact-word captions, elaborate transitions, full timeline manipulation, social publishing, and automatic video generation are outside the baseline. Muse outputs are validated data, never shell commands. Reference observations are proposed interpretations rather than a promise to recover a video's hidden editing settings.

Remotion 4.0.539 renders original SVG/React graphics from four allowlisted templates: glasses, classroom, document stack, and a stylized browser mockup. Model text is passed as escaped props; the model cannot supply executable components or external asset URLs. Rendered frames are cached by template version, props, and duration. See [Remotion's licence](https://www.remotion.dev/docs/license/pricing); its free tier covers individuals and companies of up to three people, with different terms for larger organizations. This independent demo does not copy the reference's logos or screenshots. The lockfile overrides a vulnerable transitive Zod release with 4.6.7; the graphics dependency audit passes.
