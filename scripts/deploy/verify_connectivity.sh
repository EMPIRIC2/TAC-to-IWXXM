#!/usr/bin/env bash
# H0c + H4 + H5 connectivity verification (staging / post-deploy).
# See docs/deploy.md §Runbook and .cursor/skills/connectivity-gates.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

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
  echo "== H4: skipped (set STAGING_API_URL and STAGING_FRONTEND_ORIGIN for live CORS) =="
fi

if [[ -n "${STAGING_FRONTEND_URL:-}" && -n "${VITE_API_BASE_URL:-}" ]]; then
  echo ""
  echo "== H5: Frontend bundle API URL check =="
  bundle_html="$(curl -sfL "${STAGING_FRONTEND_URL}/")"
  if [[ "$bundle_html" == *"${VITE_API_BASE_URL}"* ]]; then
    echo "OK: deployed bundle references VITE_API_BASE_URL=${VITE_API_BASE_URL}"
  else
    echo "WARN: bundle at ${STAGING_FRONTEND_URL} may not embed ${VITE_API_BASE_URL}"
    echo "      Rebuild frontend after API URL is known (docs/deploy.md §Redeploy order)."
    exit 1
  fi
else
  echo ""
  echo "== H5: skipped (set STAGING_FRONTEND_URL and VITE_API_BASE_URL for bundle check) =="
fi

echo ""
echo "Connectivity verification complete."
