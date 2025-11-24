# Backend service Dockerfile (src layout, uv install)
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install minimal deps and uv
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy project metadata first for layer caching
COPY backend/pyproject.toml ./pyproject.toml

# Copy only source and required data (GIFTs for conversion)
COPY backend/src ./src
COPY GIFTs ./GIFTs

# Install backend package into system env
RUN uv pip install --system .

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["python", "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
