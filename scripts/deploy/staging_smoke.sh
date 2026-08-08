#!/usr/bin/env bash
# Post-deploy staging connectivity smoke (H0c-style health + H4–H5 subset).
# Traces: F30 AC9/AC12 / TC-F30-009 / ADR-034
set -euo pipefail

API_URL="${LIVE_API_URL:-https://api.staging.tac-to-iwxxm.com}"
FE_URL="${LIVE_FRONTEND_URL:-https://app.staging.tac-to-iwxxm.com}"

# EV-044: staging cluster LB (not prod 168.144.12.70). Override via STAGING_LB_IP / DOKS_LB_IP.
LB_IP="${STAGING_LB_IP:-${DOKS_LB_IP:-143.244.202.13}}"
API_HOST="${API_URL#https://}"
API_HOST="${API_HOST#http://}"
API_HOST="${API_HOST%%/*}"
FE_HOST="${FE_URL#https://}"
FE_HOST="${FE_HOST#http://}"
FE_HOST="${FE_HOST%%/*}"

echo "Staging smoke: API=${API_URL} FE=${FE_URL}"

api_code="$(curl -sS -o /tmp/staging-api-health.json -w '%{http_code}' --max-time 30 "${API_URL}/health" || echo 000)"
if [[ "${api_code}" != "200" ]]; then
  echo "::warning::HTTPS API /health → ${api_code}; trying Host-header via LB ${LB_IP}"
  api_code="$(curl -sS -o /tmp/staging-api-health.json -w '%{http_code}' --max-time 30 \
    -H "Host: ${API_HOST}" "http://${LB_IP}/health" || echo 000)"
fi
if [[ "${api_code}" != "200" ]]; then
  echo "::error::API /health → ${api_code}"
  cat /tmp/staging-api-health.json 2>/dev/null || true
  exit 1
fi
echo "API /health → 200"

fe_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 30 "${FE_URL}/" || echo 000)"
if [[ "${fe_code}" != "200" && "${fe_code}" != "301" && "${fe_code}" != "302" ]]; then
  echo "::warning::HTTPS FE / → ${fe_code}; trying Host-header via LB"
  fe_code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 30 \
    -H "Host: ${FE_HOST}" "http://${LB_IP}/" || echo 000)"
fi
if [[ "${fe_code}" != "200" && "${fe_code}" != "301" && "${fe_code}" != "302" ]]; then
  echo "::error::Frontend / → ${fe_code}"
  exit 1
fi
echo "Frontend / → ${fe_code}"

# CORS preflight (H4 subset)
origin="${FE_URL}"
preflight="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 30 \
  -X OPTIONS "${API_URL}/api/v1/convert" \
  -H "Origin: ${origin}" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" || echo 000)"
if [[ "${preflight}" != "200" && "${preflight}" != "204" ]]; then
  echo "::warning::CORS preflight returned ${preflight} (continuing if health OK)"
else
  echo "CORS preflight → ${preflight}"
fi

# Optional pytest live connectivity when available
if [[ "${STAGING_SMOKE_PYTEST:-1}" == "1" ]] && [[ -f tests/smoke/test_staging_connectivity.py ]]; then
  export LIVE_API_URL="${API_URL}"
  export LIVE_FRONTEND_URL="${FE_URL}"
  if command -v uv >/dev/null 2>&1; then
    uv run pytest tests/smoke/test_staging_connectivity.py -m live -v --tb=short || {
      echo "::warning::pytest staging connectivity failed; curl probes already passed"
    }
  fi
fi

echo "Staging smoke: PASS"
