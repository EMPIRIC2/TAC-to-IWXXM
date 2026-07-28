#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

load_repo_env() {
  local env_file="${ROOT_DIR}/.env"
  local line key value

  if [[ ! -f "${env_file}" ]]; then
    return 0
  fi

  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line%%#*}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "${line}" || "${line}" != *=* ]] && continue

    key="${line%%=*}"
    key="${key%"${key##*[![:space:]]}"}"
    value="${line#*=}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value//$'\r'/}"

    if [[ -n "${key}" && -z "${!key+x}" ]]; then
      export "${key}=${value}"
    fi
  done < "${env_file}"
}

PIDS=()
NPM_BIN=""
AUTO_KILL_PORTS="${AUTO_KILL_PORTS:-prompt}"

usage() {
  cat <<'EOF'
Usage: ./start-dev-servers.sh [OPTION]

Options:
  --kill, -k      Automatically kill processes using required ports.
  --no-kill       Never kill conflicting processes (fail fast).
  --prompt        Prompt before killing conflicting processes (default).
  --help, -h      Show this help message.
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --kill|-k)
        AUTO_KILL_PORTS="true"
        ;;
      --no-kill)
        AUTO_KILL_PORTS="false"
        ;;
      --prompt)
        AUTO_KILL_PORTS="prompt"
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        echo "Error: unknown option '$1'." >&2
        usage >&2
        exit 1
        ;;
    esac
    shift
  done
}

require_command() {
  local cmd="$1"
  local hint="$2"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Error: '${cmd}' is required. ${hint}" >&2
    exit 1
  fi
}

list_listening_pids_on_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"${port}" -sTCP:LISTEN 2>/dev/null | sort -u
  fi
}

check_and_handle_port() {
  local port="$1"
  local pid process_name answer
  local port_pids=""

  while true; do
    port_pids="$(list_listening_pids_on_port "${port}" || true)"
    if [[ -z "${port_pids}" ]]; then
      return 0
    fi

    while IFS= read -r pid; do
      [[ -z "${pid}" ]] && continue
      process_name="$(ps -p "${pid}" -o comm= 2>/dev/null | xargs || echo unknown)"

      if [[ "${AUTO_KILL_PORTS}" == "true" ]]; then
        echo "Port ${port} is in use by PID ${pid} (${process_name}). Killing process..."
        kill "${pid}" 2>/dev/null || true
        sleep 1
        if kill -0 "${pid}" 2>/dev/null; then
          echo "PID ${pid} did not exit after SIGTERM. Sending SIGKILL..."
          kill -9 "${pid}" 2>/dev/null || true
        fi
        continue
      fi

      if [[ "${AUTO_KILL_PORTS}" == "false" ]]; then
        echo "Error: port ${port} is already in use by PID ${pid} (${process_name})." >&2
        echo "Set AUTO_KILL_PORTS=true to auto-kill or AUTO_KILL_PORTS=prompt for interactive prompts." >&2
        exit 1
      fi

      if [[ -t 0 ]]; then
        while true; do
          read -r -p "Port ${port} is in use by PID ${pid} (${process_name}). Kill it? [y/N]: " answer
          case "${answer}" in
            [yY]|[yY][eE][sS])
              kill "${pid}" 2>/dev/null || true
              sleep 1
              if kill -0 "${pid}" 2>/dev/null; then
                echo "PID ${pid} did not exit after SIGTERM. Sending SIGKILL..."
                kill -9 "${pid}" 2>/dev/null || true
              fi
              break
              ;;
            [nN]|[nN][oO]|"")
              echo "Keeping PID ${pid}. Exiting to avoid port conflict." >&2
              exit 1
              ;;
            *)
              echo "Please answer y or n."
              ;;
          esac
        done
      else
        echo "Error: port ${port} is already in use by PID ${pid} (${process_name})." >&2
        echo "Non-interactive shell detected; rerun with --kill (or AUTO_KILL_PORTS=true) to auto-kill." >&2
        exit 1
      fi
    done <<< "${port_pids}"
  done
}

preflight_ports() {
  check_and_handle_port 18001
  check_and_handle_port 18000
}

install_node_npm_user_space() {
  local node_version arch base_dir archive url original_dir

  original_dir="$PWD"

  node_version="v20.20.0"
  arch="$(uname -m)"
  case "${arch}" in
    x86_64) arch="x64" ;;
    aarch64|arm64) arch="arm64" ;;
    *)
      return 1
      ;;
  esac

  base_dir="$HOME/.local/node"
  archive="node-${node_version}-linux-${arch}-musl.tar.xz"
  url="https://unofficial-builds.nodejs.org/download/release/${node_version}/${archive}"

  mkdir -p "${base_dir}" "$HOME/.local/bin"
  cd "${base_dir}"

  if ! curl -fsSL "${url}" -o "${archive}"; then
    cd "${original_dir}"
    return 1
  fi

  tar -xJf "${archive}"
  ln -sfn "node-${node_version}-linux-${arch}-musl" current
  ln -sfn "${base_dir}/current/bin/node" "$HOME/.local/bin/node"
  ln -sfn "${base_dir}/current/bin/npm" "$HOME/.local/bin/npm"
  export PATH="$HOME/.local/bin:$HOME/.local/node/current/bin:/usr/local/bin:/usr/bin:$PATH"
  cd "${original_dir}"

  return 0
}

ensure_node_npm() {
  local npm_candidate

  export PATH="$HOME/.local/bin:$HOME/.local/node/current/bin:/usr/local/bin:/usr/bin:$PATH"

  npm_candidate="$(command -v npm 2>/dev/null || true)"
  if [[ -n "${npm_candidate}" ]]; then
    NPM_BIN="${npm_candidate}"
    return 0
  fi

  for npm_candidate in "$HOME/.local/bin/npm" "$HOME/.local/node/current/bin/npm" \
    "/usr/local/bin/npm" "/usr/bin/npm"; do
    if [[ -x "${npm_candidate}" ]]; then
      NPM_BIN="${npm_candidate}"
      return 0
    fi
  done

  if [[ -x "$HOME/.local/node/current/bin/npm" && -x "$HOME/.local/node/current/bin/node" ]]; then
    mkdir -p "$HOME/.local/bin"
    ln -sfn "$HOME/.local/node/current/bin/node" "$HOME/.local/bin/node"
    ln -sfn "$HOME/.local/node/current/bin/npm" "$HOME/.local/bin/npm"
    npm_candidate="$(command -v npm 2>/dev/null || true)"
    if [[ -n "${npm_candidate}" ]]; then
      NPM_BIN="${npm_candidate}"
      return 0
    fi
  fi

  echo "npm not found. Attempting user-space Node.js install..."
  if install_node_npm_user_space; then
    npm_candidate="$(command -v npm 2>/dev/null || true)"
    if [[ -n "${npm_candidate}" ]]; then
      NPM_BIN="${npm_candidate}"
      return 0
    fi
  fi

  if command -v apk >/dev/null 2>&1 && [[ "$(id -u)" -eq 0 ]]; then
    echo "npm not found. Installing Node.js and npm via apk..."
    apk add --no-cache nodejs npm
    npm_candidate="$(command -v npm 2>/dev/null || true)"
    if [[ -n "${npm_candidate}" ]]; then
      NPM_BIN="${npm_candidate}"
      return 0
    fi
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

parse_args "$@"

load_repo_env

# F21: DISABLE_AUTH / api.disableAuth retired — public app by default.
sync_disable_auth_from_config() {
  unset DISABLE_AUTH 2>/dev/null || true
}

trap cleanup INT TERM EXIT

run_backend() {
  local backend_dir="${ROOT_DIR}/apps/backend"

  if [[ ! -d "${backend_dir}" ]]; then
    echo "Error: monorepo backend not found at ${backend_dir}" >&2
    exit 1
  fi

  cd "${backend_dir}"

  if ! command -v uv >/dev/null 2>&1; then
    echo "Error: uv is required to run apps/backend (install via make install)." >&2
    exit 1
  fi

  export METAR_CONFIG_ENV="${METAR_CONFIG_ENV:-local}"
  export SUPABASE_PUBLISHABLE_KEY="${SUPABASE_PUBLISHABLE_KEY:-${SUPABASE_ANON_KEY:-}}"

  uv run uvicorn src.api:app --reload --host 0.0.0.0 --port 18001
}

run_frontend() {
  local frontend_dir="${ROOT_DIR}/apps/frontend"

  if [[ ! -d "${frontend_dir}" ]]; then
    echo "Error: monorepo frontend not found at ${frontend_dir}" >&2
    exit 1
  fi

  cd "${frontend_dir}"

  ensure_node_npm

  if ! command -v pnpm >/dev/null 2>&1; then
    echo "Error: pnpm is required to run apps/frontend (install via make install)." >&2
    exit 1
  fi

  if [[ ! -d "node_modules" ]]; then
    echo "Installing frontend dependencies..."
    pnpm install
  fi

  export METAR_CONFIG_ENV="${METAR_CONFIG_ENV:-local}"
  export SUPABASE_PUBLISHABLE_KEY="${SUPABASE_PUBLISHABLE_KEY:-${SUPABASE_ANON_KEY:-}}"

  bash "${ROOT_DIR}/scripts/frontend/prepare-config.sh"

  pnpm exec vite --host 0.0.0.0 --port 18000
}

preflight_ports

sync_disable_auth_from_config

echo "Starting merged API (backend + auth) on :18001 (reload enabled)..."
run_backend &
PIDS+=("$!")

echo "Starting frontend on :18000 (Vite dev server)..."
run_frontend &
PIDS+=("$!")

echo "All development servers started. Press Ctrl+C to stop all."
wait
