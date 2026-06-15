# Auth service Dockerfile (src layout, using uv for install)
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Install minimal build deps, uv, and dns utilities
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy project metadata first for better layer caching
COPY auth/pyproject.toml ./

# Copy environment configuration files (development/testing)
# NOTE: .env with secrets should be provided at runtime, not baked into image
# For Docker:
#   - Local development: mount .env file with -v or use docker-compose
#   - Production: use Docker secrets, environment variables, or cloud secret management
# This copies .env and .env.example if they exist
COPY auth/.env* ./

# Copy only necessary source (avoid copying venv, caches)
COPY auth/src ./src

# Install the package with uv into the system environment
RUN uv pip install --system .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck using the new /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["python", "-m", "uvicorn", "auth.__main__:app", "--host", "0.0.0.0", "--port", "8000"]
