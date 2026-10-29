FROM ghcr.io/astral-sh/uv:0.9.6 AS uv
FROM node:22-bookworm-slim AS sam-runtime
WORKDIR /sam
COPY backend/package.json backend/package-lock.json backend/.npmrc ./
RUN npm ci --ignore-scripts
FROM python:3.12-slim
COPY --from=uv /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 reelos \
    && mkdir /data && chown reelos:reelos /data
COPY --from=sam-runtime /usr/local/bin/node /usr/local/bin/node
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
COPY backend/reelos ./reelos
COPY backend/scripts ./scripts
COPY --from=sam-runtime /sam/node_modules ./node_modules
RUN uv sync --frozen --no-dev
ENV REELOS_DATA_DIR=/data PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER reelos
EXPOSE 8000
CMD ["/app/backend/.venv/bin/uvicorn", "reelos.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
