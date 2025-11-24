# Auth service Dockerfile (optional standalone)
FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY auth/pyproject.toml auth/pyproject.toml
COPY auth/ auth/

RUN pip install --no-cache-dir auth/

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8100
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8100/auth/login').read()" || exit 1

CMD ["python", "-m", "uvicorn", "auth.__main__:app", "--host", "0.0.0.0", "--port", "8100"]
