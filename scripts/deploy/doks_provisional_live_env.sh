#!/usr/bin/env bash
# Export LIVE_* / Playwright env for provisional DOKS (D-S038-t63-waive).
# Browser resolves placeholder hosts via Chromium --host-resolver-rules (no /etc/hosts).
# API request fixture uses LB IP + Host header (Node does not use Chromium DNS).
#
# Always overwrites LIVE_* / PLAYWRIGHT_* so Makefile Render defaults and local
# .env PLAYWRIGHT_BASE_URL cannot pin the wrong target.
#
# Usage:
#   source scripts/deploy/doks_provisional_live_env.sh
#   make test-live-e2e-doks-provisional
#   make test-live-connectivity-doks-provisional
set -euo pipefail

LB_IP="${DOKS_LB_IP:-168.144.12.70}"
API_HOST="${DOKS_API_HOST:-api.doks.placeholder.metar-iwxxm.local}"
FE_HOST="${DOKS_FE_HOST:-app.doks.placeholder.metar-iwxxm.local}"

export DOKS_LB_IP="${LB_IP}"
export DOKS_API_HOST="${API_HOST}"
export DOKS_FE_HOST="${FE_HOST}"
export PLAYWRIGHT_DOKS_PROVISIONAL=1

# FE origin must be the placeholder Host (Ingress + CORS).
export LIVE_FRONTEND_URL="http://${FE_HOST}"
export PLAYWRIGHT_BASE_URL="http://${FE_HOST}"

# Node/Playwright request fixture hits LB IP; Host header added in helpers.
export LIVE_API_URL="http://${LB_IP}"
export PLAYWRIGHT_API_BASE_URL="http://${LB_IP}"
export VITE_API_BASE_URL="http://${API_HOST}"
export STAGING_API_URL="${LIVE_API_URL}"
export STAGING_FRONTEND_URL="${LIVE_FRONTEND_URL}"
export STAGING_FRONTEND_ORIGIN="${LIVE_FRONTEND_URL}"
export RUN_LIVE_TESTS=1
export DISABLE_AUTH=false

# Prefer E2E_USER_*; fall back to ADMIN_* from .env (loaded by Playwright / Makefile).
if [[ -z "${E2E_USER_EMAIL:-}" && -n "${ADMIN_EMAIL:-}" ]]; then
  export E2E_USER_EMAIL="${ADMIN_EMAIL}"
fi
if [[ -z "${E2E_USER_PASSWORD:-}" && -n "${ADMIN_PASSWORD:-}" ]]; then
  export E2E_USER_PASSWORD="${ADMIN_PASSWORD}"
fi

echo "DOKS provisional live env:"
echo "  LIVE_FRONTEND_URL=${LIVE_FRONTEND_URL}"
echo "  LIVE_API_URL=${LIVE_API_URL} (Host: ${API_HOST})"
echo "  PLAYWRIGHT_DOKS_PROVISIONAL=1 LB=${LB_IP}"
echo "  E2E_USER_EMAIL=${E2E_USER_EMAIL:-<unset>}"
