FROM ghcr.io/astral-sh/uv:0.9.6 AS uv
FROM node:22-bookworm-slim AS sam-runtime
WORKDIR /sam
COPY backend/package.json backend/package-lock.json backend/.npmrc ./
RUN npm ci --ignore-scripts
FROM node:22-bookworm-slim AS graphics-runtime
WORKDIR /graphics
COPY graphics/package.json graphics/package-lock.json graphics/.npmrc ./
RUN npm ci --ignore-scripts
COPY graphics/src ./src
COPY graphics/render.mjs ./
COPY graphics/hyperframes ./hyperframes
COPY graphics/montage ./montage
RUN node --input-type=module -e "import {ensureBrowser} from '@remotion/renderer'; await ensureBrowser({logLevel:'error'});"
# HyperFrames reuses Remotion's headless Chrome; a relative link survives the copy to /app/graphics.
RUN ln -s "$(find node_modules/.remotion -name headless_shell -type f | head -1)" headless_shell \
    && test -x headless_shell
RUN node --input-type=module -e "import {bundle} from '@remotion/bundler'; await bundle({entryPoint:'/graphics/src/index.tsx',outDir:'/graphics/bundle',enableCaching:false});"
FROM python:3.12-slim-bookworm
COPY --from=uv /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core \
    libnss3 libdbus-1-3 libatk1.0-0 libgbm1 libasound2 libxrandr2 libxkbcommon0 \
    libxfixes3 libxcomposite1 libxdamage1 libatk-bridge2.0-0 libpango-1.0-0 libcairo2 libcups2 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 reelos \
    && mkdir /data && chown reelos:reelos /data
COPY --from=sam-runtime /usr/local/bin/node /usr/local/bin/node
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
COPY backend/reelos ./reelos
COPY backend/scripts ./scripts
COPY --from=sam-runtime /sam/node_modules ./node_modules
COPY --from=graphics-runtime /graphics /app/graphics
RUN uv sync --frozen --no-dev
ENV REELOS_DATA_DIR=/data PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    HYPERFRAMES_BROWSER_PATH=/app/graphics/headless_shell
USER reelos
EXPOSE 8000
CMD ["/app/backend/.venv/bin/uvicorn", "reelos.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
