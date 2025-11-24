# Frontend GUI service Dockerfile
FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Copy component pyprojects and source needed for GUI (gui + auth + backend logic + GIFTs)
COPY gui/pyproject.toml gui/pyproject.toml
COPY auth/pyproject.toml auth/pyproject.toml
COPY backend/pyproject.toml backend/pyproject.toml
COPY gui/ gui/
COPY auth/ auth/
COPY backend/ backend/
COPY GIFTs/ GIFTs/

# Install dependencies from each component
RUN pip install --no-cache-dir backend/ auth/ gui/

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

ENV BACKEND_URL=http://backend:8000
CMD ["python", "-m", "uvicorn", "gui.app:app", "--host", "0.0.0.0", "--port", "8000"]
