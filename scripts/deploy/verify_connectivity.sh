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
  frontend_base="${STAGING_FRONTEND_URL%/}"
  bundle_html="$(curl -sfL "${frontend_base}/")"

  # Vite embeds build-time env vars in JS chunks, not index.html.
  mapfile -t asset_paths < <(
    printf '%s\n' "$bundle_html" \
      | grep -oE '(src|href)="(/assets/[^"]+\.(js|css))"' \
      | sed -E 's/^(src|href)="([^"]+)"$/\2/' \
      | sort -u
  )

  bundle_content="$bundle_html"
  for asset_path in "${asset_paths[@]}"; do
    bundle_content+="$(curl -sfL "${frontend_base}${asset_path}")"
  done

  if [[ "$bundle_content" == *"${VITE_API_BASE_URL}"* ]]; then
    echo "OK: deployed bundle references VITE_API_BASE_URL=${VITE_API_BASE_URL}"
  else
    echo "WARN: bundle at ${STAGING_FRONTEND_URL} may not embed ${VITE_API_BASE_URL}"
    echo "      Rebuild frontend after API URL is known (docs/deploy.md §Redeploy order)."
    exit 1
  fi

  deprecated_urls=(
    "metar-to-iwxxm-auth-v2.onrender.com"
    "VITE_BACKEND_URL"
    "VITE_AUTH_SERVICE_URL"
  )
  for deprecated in "${deprecated_urls[@]}"; do
    if [[ "$bundle_content" == *"${deprecated}"* ]]; then
      echo "WARN: deployed bundle still references deprecated ${deprecated}"
      echo "      Rebuild frontend from monorepo main (unified VITE_API_BASE_URL per ADR-002)."
      exit 1
    fi
  done
else
  echo ""
  echo "== H5: skipped (set STAGING_FRONTEND_URL and VITE_API_BASE_URL for bundle check) =="
fi

echo ""
echo "Connectivity verification complete."
