#!/usr/bin/env bash
# DOKS provisional cutover smoke (T6.3 waive / T6.4) — LB IP + Ingress Host headers.
# Real DNS deferred (D-S038-t63-waive). See docs/ops/doks-cutover-soak-checklist.md.
set -euo pipefail

LB_IP="${DOKS_LB_IP:-168.144.12.70}"
API_HOST="${DOKS_API_HOST:-api.doks.placeholder.metar-iwxxm.local}"
FE_HOST="${DOKS_FE_HOST:-app.doks.placeholder.metar-iwxxm.local}"
BASE="http://${LB_IP}"

pass=0
fail=0

check() {
  local name="$1"
  local expect="$2"
  local got="$3"
  if [[ "$got" == "$expect" ]]; then
    echo "PASS  ${name} (HTTP ${got})"
    pass=$((pass + 1))
  else
    echo "FAIL  ${name} (expected ${expect}, got ${got})"
    fail=$((fail + 1))
  fi
}

echo "== DOKS Host-header smoke =="
echo "LB=${LB_IP} API_HOST=${API_HOST} FE_HOST=${FE_HOST}"
echo ""

code="$(curl -sS -o /tmp/doks-smoke-health.json -w '%{http_code}' \
  -H "Host: ${API_HOST}" "${BASE}/health")"
check "API /health" "200" "$code"

code="$(curl -sS -o /tmp/doks-smoke-convert.json -w '%{http_code}' \
  -H "Host: ${API_HOST}" \
  -H "Content-Type: application/json" \
  -X POST "${BASE}/api/v1/convert" \
  -d '{"metars":["METAR KJFK 031951Z 18010KT 10SM FEW050 22/12 A3012"]}')"
check "API POST /api/v1/convert" "200" "$code"

# FE may 502 briefly during Ingress endpoint churn after rollout.
fe_code=""
for attempt in 1 2 3 4 5; do
  fe_code="$(curl -sS -o /tmp/doks-smoke-fe.html -w '%{http_code}' \
    -H "Host: ${FE_HOST}" "${BASE}/" || echo "000")"
  [[ "$fe_code" == "200" ]] && break
  sleep 2
done
check "FE /" "200" "$fe_code"

code="$(curl -sS -o /tmp/doks-smoke-config.json -w '%{http_code}' \
  -H "Host: ${FE_HOST}" "${BASE}/config.json")"
check "FE /config.json" "200" "$code"

# CORS preflight (H4-lite): Origin must be reflected when ConfigMap allows it.
cors_origin="$(curl -sS -D - -o /dev/null -X OPTIONS \
  -H "Host: ${API_HOST}" \
  -H "Origin: http://${FE_HOST}" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  "${BASE}/api/v1/convert" | tr -d '\r' | awk -F': ' 'tolower($1)=="access-control-allow-origin"{print $2; exit}')"
if [[ "$cors_origin" == "http://${FE_HOST}" || "$cors_origin" == "http://${LB_IP}" ]]; then
  echo "PASS  CORS preflight Allow-Origin=${cors_origin}"
  pass=$((pass + 1))
else
  echo "FAIL  CORS preflight Allow-Origin=${cors_origin:-<missing>}"
  fail=$((fail + 1))
fi

if [[ -f /tmp/doks-smoke-config.json ]]; then
  api_base="$(python3 -c 'import json; print(json.load(open("/tmp/doks-smoke-config.json")).get("api",{}).get("baseUrl",""))')"
  echo "INFO  FE config.json api.baseUrl=${api_base}"
fi

echo ""
echo "Result: ${pass} passed, ${fail} failed"
if [[ "$fail" -gt 0 ]]; then
  exit 1
fi

cat <<EOF

Operator LIVE_* pin (provisional — requires /etc/hosts → ${LB_IP}):
  export LIVE_API_URL=http://${API_HOST}
  export LIVE_FRONTEND_URL=http://${FE_HOST}
  export VITE_API_BASE_URL=\${LIVE_API_URL}

/etc/hosts:
  ${LB_IP}  ${API_HOST} ${FE_HOST}
EOF
