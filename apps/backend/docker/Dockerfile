# Backend API Dockerfile — monorepo root context (deploy.md §Docker Build Context)
# Builder installs iwxxm-validate PyO3 so IWXXM 2025-2 Schematron (xslt2) runs
# instead of lxml SCHEMATRON_SKIPPED. [Corpus: product §F13] [Corpus: deploy]
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH="/usr/local/cargo/bin:/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
        ca-certificates \
        build-essential \
        pkg-config \
        libxml2-dev \
        libxslt1-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \
        | sh -s -- -y --default-toolchain stable --profile minimal

# Workspace metadata (layer cache)
COPY pyproject.toml uv.lock ./
COPY packages/shared/pyproject.toml packages/shared/pyproject.toml
COPY packages/auth/pyproject.toml packages/auth/pyproject.toml
COPY packages/tac2iwxxm/pyproject.toml packages/tac2iwxxm/pyproject.toml
COPY packages/reference-lookup/pyproject.toml packages/reference-lookup/pyproject.toml
COPY packages/tac-decoding/pyproject.toml packages/tac-decoding/pyproject.toml
COPY packages/iwxxm-validate/pyproject.toml packages/iwxxm-validate/pyproject.toml
COPY packages/tac-validate/pyproject.toml packages/tac-validate/pyproject.toml
COPY packages/dissemination/pyproject.toml packages/dissemination/pyproject.toml
COPY apps/backend/pyproject.toml apps/backend/pyproject.toml

# Workspace sources required at runtime / native build
COPY packages/shared packages/shared
COPY packages/auth packages/auth
COPY packages/tac2iwxxm packages/tac2iwxxm
COPY packages/reference-lookup packages/reference-lookup
COPY packages/tac-decoding packages/tac-decoding
COPY packages/iwxxm-validate packages/iwxxm-validate
COPY packages/tac-validate packages/tac-validate
COPY packages/dissemination packages/dissemination
COPY apps/backend apps/backend
COPY config config
COPY vendor/schemas vendor/schemas
# EV-933 — ConversionProfile inspector reads docs/domain/profiles/catalog.yaml
COPY docs/domain/profiles docs/domain/profiles

# Backend still resolves schemas/iwxxm; vendor tree is authoritative (ADR-001).
RUN ln -s /app/vendor/schemas /app/schemas

# Install API package, then bake iwxxm-validate._rust (F13 Schematron for 2025-2).
RUN uv sync --frozen --no-dev --package metar-backend \
    && uv pip install 'maturin==1.14.1' \
    && (cd packages/iwxxm-validate \
        && uv run maturin develop --release --manifest-path rust/Cargo.toml --uv) \
    && python -c "from iwxxm_validate import rust_available; assert rust_available(), 'iwxxm_validate._rust missing'" \
    && rm -rf packages/iwxxm-validate/rust/target packages/tac2iwxxm/rust/target \
        /usr/local/cargo/registry /usr/local/rustup

# --- runtime (no Rust toolchain) ---
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    IWXXM_PROJECT_ROOT=/app \
    IWXXM_SCHEMAS_ROOT=/app/vendor/schemas/iwxxm \
    PORT=8000 \
    RELOAD=false \
    HOST=0.0.0.0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        libxml2 \
        libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/apps/backend

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["python", "-m", "src"]
