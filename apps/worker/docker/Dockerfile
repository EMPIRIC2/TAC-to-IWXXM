# F8 ingest worker — monorepo root context (ADR-018)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        libxml2 \
        libxslt1.1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
COPY packages/shared/pyproject.toml packages/shared/pyproject.toml
COPY packages/tac2iwxxm/pyproject.toml packages/tac2iwxxm/pyproject.toml
COPY packages/iwxxm-validate/pyproject.toml packages/iwxxm-validate/pyproject.toml
COPY packages/tac-validate/pyproject.toml packages/tac-validate/pyproject.toml
COPY apps/worker/pyproject.toml apps/worker/pyproject.toml

COPY packages/shared packages/shared
COPY packages/tac2iwxxm packages/tac2iwxxm
COPY packages/iwxxm-validate packages/iwxxm-validate
COPY packages/tac-validate packages/tac-validate
COPY apps/worker apps/worker
COPY vendor/schemas vendor/schemas

RUN ln -s /app/vendor/schemas /app/schemas \
    && uv sync --frozen --no-dev --package metar-worker

ENV PATH="/app/.venv/bin:$PATH" \
    IWXXM_PROJECT_ROOT=/app \
    IWXXM_SCHEMAS_ROOT=/app/vendor/schemas/iwxxm

CMD ["python", "-m", "metar_worker"]
