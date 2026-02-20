#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PIDS=()

require_command() {
  local cmd="$1"
  local hint="$2"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Error: '${cmd}' is required. ${hint}" >&2
    exit 1
  fi
}

ensure_node_npm() {
  if command -v npm >/dev/null 2>&1; then
    return 0
  fi

  if command -v apk >/dev/null 2>&1 && [[ "$(id -u)" -eq 0 ]]; then
    echo "npm not found. Installing Node.js and npm via apk..."
    apk add --no-cache nodejs npm
    return 0
  fi

  echo "Error: npm is not installed." >&2
  echo "Install Node.js + npm to run the required frontend dev server." >&2
  echo "If using Alpine as root: apk add --no-cache nodejs npm" >&2
  exit 1
}

ensure_python_service() {
  local service_dir="$1"

  require_command python3 "Install Python 3 and ensure it is on PATH."

  cd "${service_dir}"

  if [[ ! -x ".venv/bin/python" ]]; then
    rm -rf .venv
    echo "Creating virtual environment in ${service_dir}/.venv..."
    python3 -m venv .venv
  fi

  if ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
    echo "Recreating broken virtual environment in ${service_dir}/.venv..."
    rm -rf .venv
    python3 -m venv .venv
  fi

  if ! .venv/bin/python -c "import uvicorn" >/dev/null 2>&1; then
    echo "Installing Python dependencies for ${service_dir}..."
    .venv/bin/python -m pip install -e .
  fi
}

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
  ensure_python_service "${ROOT_DIR}/backend"

  if ! .venv/bin/python -c "import requests" >/dev/null 2>&1; then
    echo "Installing missing backend dependency 'requests'..."
    .venv/bin/python -m pip install -e .
  fi

  .venv/bin/python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8001
}

run_auth() {
  ensure_python_service "${ROOT_DIR}/auth"
  .venv/bin/python -m uvicorn src.__main__:app --reload --host 0.0.0.0 --port 8003
}

run_frontend() {
  cd "${ROOT_DIR}/frontend"

  ensure_node_npm

  if [[ ! -d "node_modules" ]]; then
    echo "Installing frontend dependencies..."
    npm install
  fi

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
