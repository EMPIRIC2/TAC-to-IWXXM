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

# Install both the backend package and GIFTs library into system env
RUN uv pip install --system . && \
    uv pip install --system ./GIFTs

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Run backend as a module (entry point will be: src package)
ENV PORT=8000 RELOAD=false
CMD ["python", "-m", "src"]

