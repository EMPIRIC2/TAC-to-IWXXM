# Backend API Dockerfile — monorepo root context (deploy.md §Docker Build Context)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# System deps for lxml/schematron and uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
        ca-certificates \
        libxml2 \
        libxslt1.1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Workspace metadata (layer cache)
COPY pyproject.toml uv.lock ./
COPY packages/shared/pyproject.toml packages/shared/pyproject.toml
COPY packages/tac2iwxxm/pyproject.toml packages/tac2iwxxm/pyproject.toml
COPY packages/iwxxm-validate/pyproject.toml packages/iwxxm-validate/pyproject.toml
COPY packages/tac-validate/pyproject.toml packages/tac-validate/pyproject.toml
COPY packages/dissemination/pyproject.toml packages/dissemination/pyproject.toml
COPY apps/backend/pyproject.toml apps/backend/pyproject.toml

# Workspace sources required at runtime
COPY packages/shared packages/shared
COPY packages/tac2iwxxm packages/tac2iwxxm
COPY packages/iwxxm-validate packages/iwxxm-validate
COPY packages/tac-validate packages/tac-validate
COPY packages/dissemination packages/dissemination
COPY apps/backend apps/backend
COPY config config
COPY vendor/schemas vendor/schemas

# Backend still resolves schemas/iwxxm; vendor tree is authoritative (ADR-001).
RUN ln -s /app/vendor/schemas /app/schemas

# Install API package and workspace deps into workspace .venv
RUN uv sync --frozen --no-dev --package metar-backend

ENV PATH="/app/.venv/bin:$PATH"

ENV IWXXM_PROJECT_ROOT=/app \
    IWXXM_SCHEMAS_ROOT=/app/vendor/schemas/iwxxm \
    PORT=8000 \
    RELOAD=false \
    HOST=0.0.0.0

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/apps/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["python", "-m", "src"]
