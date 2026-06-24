#!/usr/bin/env bash
# H0c + H4 + H5 connectivity verification (staging / post-deploy).
# See docs/deploy.md §Runbook and .cursor/skills/connectivity-gates.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Prefer canonical LIVE_* env vars; map to legacy STAGING_* for backward compatibility.
LIVE_API_URL="${LIVE_API_URL:-${STAGING_API_URL:-}}"
LIVE_FRONTEND_URL="${LIVE_FRONTEND_URL:-${STAGING_FRONTEND_ORIGIN:-${STAGING_FRONTEND_URL:-}}}"
export STAGING_API_URL="${STAGING_API_URL:-${LIVE_API_URL}}"
export STAGING_FRONTEND_ORIGIN="${STAGING_FRONTEND_ORIGIN:-${LIVE_FRONTEND_URL}}"
export STAGING_FRONTEND_URL="${STAGING_FRONTEND_URL:-${LIVE_FRONTEND_URL}}"
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-${LIVE_API_URL}}"

wake_live_api() {
  local base_url="${1:-}"
  if [[ -z "$base_url" ]]; then
    return 0
  fi
  base_url="${base_url%/}"
  local attempt
  for attempt in 1 2 3; do
    if curl -sf --max-time 30 "${base_url}/health" >/dev/null; then
      echo "Live API awake: ${base_url}"
      return 0
    fi
    if [[ "$attempt" -lt 3 ]]; then
      echo "Waiting for live API (attempt ${attempt}/3)..."
      sleep 30
    fi
  done
  echo "WARN: could not wake live API at ${base_url} — continuing anyway"
}

if [[ -n "${LIVE_API_URL}" ]]; then
  wake_live_api "${LIVE_API_URL}"
fi

echo "== H0c: CORS policy unit tests =="
if command -v uv >/dev/null 2>&1 && [[ -f pyproject.toml ]]; then
  uv run pytest tests/unit/test_cors_policy.py -v --tb=short
else
  python3 -m pytest tests/unit/test_cors_policy.py -v --tb=short
fi

if [[ -n "${STAGING_API_URL:-}" && -n "${STAGING_FRONTEND_ORIGIN:-}" ]]; then
  echo ""
  echo "== H4: Live CORS preflight =="
  if command -v uv >/dev/null 2>&1; then
    uv run pytest tests/smoke/test_staging_connectivity.py -m live -v --tb=short
  else
    python3 -m pytest tests/smoke/test_staging_connectivity.py -m live -v --tb=short
  fi
else
  echo ""
  echo "== H4: skipped (set LIVE_API_URL and LIVE_FRONTEND_URL for live CORS) =="
fi

if [[ -n "${STAGING_FRONTEND_URL:-}" && -n "${VITE_API_BASE_URL:-}" ]]; then
  echo ""
  echo "== H5: Frontend runtime config check =="
  frontend_base="${STAGING_FRONTEND_URL%/}"
  expected_api_url="${VITE_API_BASE_URL%/}"

  if ! config_json="$(curl -sfL "${frontend_base}/config.json")"; then
    echo "ERROR: could not fetch ${frontend_base}/config.json"
    exit 1
  fi

  python3 - <<'PY' "$config_json" "$expected_api_url" "$frontend_base"
import json, sys

raw, expected_api, frontend_base = sys.argv[1], sys.argv[2].rstrip("/"), sys.argv[3]
cfg = json.loads(raw)
actual_api = str(cfg.get("api", {}).get("baseUrl", "")).rstrip("/")
if actual_api != expected_api:
    raise SystemExit(
        f"config.json api.baseUrl mismatch: expected {expected_api!r}, got {actual_api!r}"
    )
if cfg.get("api", {}).get("disableAuth") is True:
    raise SystemExit("config.json api.disableAuth must be false in production")
print(f"OK: {frontend_base}/config.json api.baseUrl={actual_api}")
PY

  deprecated_refs=(
    "metar-to-iwxxm-auth-v2.onrender.com"
    "VITE_BACKEND_URL"
    "VITE_AUTH_SERVICE_URL"
  )
  for deprecated in "${deprecated_refs[@]}"; do
    if [[ "$config_json" == *"${deprecated}"* ]]; then
      echo "WARN: runtime config still references deprecated ${deprecated}"
      exit 1
    fi
  done
else
  echo ""
  echo "== H5: skipped (set LIVE_FRONTEND_URL and VITE_API_BASE_URL for runtime config check) =="
fi

echo ""
echo "Connectivity verification complete."
