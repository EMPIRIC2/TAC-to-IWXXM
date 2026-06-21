#!/usr/bin/env bash
# Apply METAR_CORS_ORIGINS + FRONTEND_URL on metar-to-iwxxm-api and trigger redeploy.
# Requires RENDER_API_KEY (https://dashboard.render.com/u/settings#api-keys).
#
# Usage:
#   export RENDER_API_KEY=rnd_...
#   bash scripts/deploy/apply_render_cors_env.sh
#
# See docs/bug-reports/BUG-2026-06-20-login-cors-failed-fetch.md
set -euo pipefail

API_BASE="https://api.render.com/v1"
SERVICE_NAME="${RENDER_SERVICE_NAME:-metar-to-iwxxm-api}"
FRONTEND_ORIGIN="${FRONTEND_ORIGIN:-https://metar-to-iwxxm-frontend-v4-web.onrender.com}"

if [[ -z "${RENDER_API_KEY:-}" && -f .env ]]; then
  RENDER_API_KEY="$(grep -E '^RENDER_API_KEY=' .env | head -1 | cut -d= -f2- | tr -d '\r\"'"'"'')"
  export RENDER_API_KEY
fi

if [[ -z "${RENDER_API_KEY:-}" ]]; then
  echo "ERROR: RENDER_API_KEY is not set." >&2
  echo "Export it or add to .env — https://dashboard.render.com/u/settings#api-keys" >&2
  exit 1
fi

auth_header=(--header "Authorization: Bearer ${RENDER_API_KEY}" --header "Accept: application/json")

echo "== Resolve service ID for ${SERVICE_NAME} =="
services_json="$(curl -sf "${auth_header[@]}" "${API_BASE}/services?limit=100")"
service_id="$(python3 - <<'PY' "$services_json" "$SERVICE_NAME"
import json, sys
data = json.loads(sys.argv[1])
name = sys.argv[2]
for item in data:
    svc = item.get("service") or item
    if svc.get("name") == name:
        print(svc["id"])
        break
PY
)"

if [[ -z "${service_id}" ]]; then
  echo "ERROR: Service ${SERVICE_NAME} not found in Render account." >&2
  exit 1
fi
echo "Service ID: ${service_id}"

set_env_var() {
  local key="$1"
  local value="$2"
  echo "== Set ${key} =="
  curl -sf "${auth_header[@]}" \
    --header "Content-Type: application/json" \
    --request PUT \
    --data "$(python3 -c "import json; print(json.dumps({'value': '''${value}'''}))")" \
    "${API_BASE}/services/${service_id}/env-vars/${key}" >/dev/null
}

set_env_var "METAR_CORS_ORIGINS" "${FRONTEND_ORIGIN}"
set_env_var "FRONTEND_URL" "${FRONTEND_ORIGIN}"

echo "== Trigger deploy =="
deploy_json="$(curl -sf "${auth_header[@]}" \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{}' \
  "${API_BASE}/services/${service_id}/deploys")"
deploy_id="$(python3 - <<'PY' "$deploy_json"
import json, sys
print(json.loads(sys.argv[1]).get("id", ""))
PY
)"
echo "Deploy started: ${deploy_id:-unknown}"

echo ""
echo "Wait for deploy to finish, then verify:"
echo "  uv run pytest tests/bugs/test_bug_2026_06_20_login_cors_failed_fetch.py -m live -v"
