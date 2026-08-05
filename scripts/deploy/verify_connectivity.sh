#!/usr/bin/env bash
# H0c + H4 + H5 connectivity verification (staging / post-deploy).
# See docs/deploy.md §Runbook and .cursor/skills/connectivity-gates.md
#
# Provisional DOKS (D-S038-t63-waive): source doks_provisional_live_env.sh first
# (or make test-live-connectivity-doks-provisional). API/FE fetches use LB IP +
# Ingress Host headers; H5 expects VITE_API_BASE_URL (placeholder API host).
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

DOKS_PROVISIONAL=0
if [[ "${PLAYWRIGHT_DOKS_PROVISIONAL:-}" == "1" || "${DOKS_PROVISIONAL:-}" == "1" ]]; then
  DOKS_PROVISIONAL=1
fi
DOKS_LB_IP="${DOKS_LB_IP:-168.144.12.70}"
DOKS_API_HOST="${DOKS_API_HOST:-api.doks.placeholder.metar-iwxxm.local}"
DOKS_FE_HOST="${DOKS_FE_HOST:-app.doks.placeholder.metar-iwxxm.local}"

api_curl_headers=()
fe_curl_headers=()
if [[ "$DOKS_PROVISIONAL" == "1" ]]; then
  api_curl_headers=(-H "Host: ${DOKS_API_HOST}")
  fe_curl_headers=(-H "Host: ${DOKS_FE_HOST}")
  # FE hostname may not resolve; fetch via LB IP + Host.
  FE_FETCH_BASE="http://${DOKS_LB_IP}"
  echo "DOKS provisional mode: LB=${DOKS_LB_IP} API_HOST=${DOKS_API_HOST} FE_HOST=${DOKS_FE_HOST}"
else
  FE_FETCH_BASE="${STAGING_FRONTEND_URL}"
fi

wake_live_api() {
  local base_url="${1:-}"
  if [[ -z "$base_url" ]]; then
    return 0
  fi
  base_url="${base_url%/}"
  local attempt
  for attempt in 1 2 3; do
    if curl -sf --max-time 30 "${api_curl_headers[@]}" "${base_url}/health" >/dev/null; then
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
  fetch_base="${FE_FETCH_BASE%/}"

  if ! config_json="$(curl -sfL "${fe_curl_headers[@]}" "${fetch_base}/config.json")"; then
    echo "ERROR: could not fetch ${fetch_base}/config.json"
    if [[ "$DOKS_PROVISIONAL" == "1" ]]; then
      echo "  (Host: ${DOKS_FE_HOST}; origin label ${frontend_base})"
    else
      echo "  (URL: ${frontend_base}/config.json)"
    fi
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
if "disableAuth" in cfg.get("api", {}):
    raise SystemExit("config.json api.disableAuth is retired (F21 public app)")
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
