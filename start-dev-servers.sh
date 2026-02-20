#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PIDS=()

cleanup() {
  echo
  echo "Stopping development servers..."
  for pid in "${PIDS[@]:-}"; do
    if [[ -n "${pid}" ]] && kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
    fi
  done
  wait || true
  echo "All servers stopped."
}

trap cleanup INT TERM EXIT

run_backend() {
  cd "${ROOT_DIR}/backend"

  if [[ -x ".venv/bin/python" ]]; then
    .venv/bin/python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8001
  else
    python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8001
  fi
}

run_auth() {
  cd "${ROOT_DIR}/auth"

  if [[ -x ".venv/bin/python" ]]; then
    .venv/bin/python -m uvicorn src.__main__:app --reload --host 0.0.0.0 --port 8003
  else
    python -m uvicorn src.__main__:app --reload --host 0.0.0.0 --port 8003
  fi
}

run_frontend() {
  cd "${ROOT_DIR}/frontend"
  npm run dev -- --host 0.0.0.0 --port 5173
}

echo "Starting backend on :8001 (reload enabled)..."
run_backend &
PIDS+=("$!")

echo "Starting auth on :8003 (reload enabled)..."
run_auth &
PIDS+=("$!")

echo "Starting frontend on :5173 (Vite dev server)..."
run_frontend &
PIDS+=("$!")

echo "All development servers started. Press Ctrl+C to stop all."
wait
