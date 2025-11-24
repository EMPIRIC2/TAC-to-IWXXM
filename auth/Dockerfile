# Auth service Dockerfile (src layout, using uv for install)
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install minimal build deps and uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy project metadata first for better layer caching
COPY pyproject.toml ./

# Copy only necessary source (avoid copying venv, caches)
COPY src ./src

# Install the package with uv into the system environment
RUN uv pip install --system .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8100

# Simple healthcheck hitting a lightweight endpoint (registration route returns 405 without body, so use root docs if mounted)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request, sys; urllib.request.urlopen('http://localhost:8100/auth/apikeys').read()" || exit 1

CMD ["python", "-m", "uvicorn", "auth.__main__:app", "--host", "0.0.0.0", "--port", "8100"]
