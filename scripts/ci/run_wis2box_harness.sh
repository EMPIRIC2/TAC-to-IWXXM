#!/usr/bin/env bash
# S019 / EV-014 T3.3 — CI Compose hook for F17 wis2box harness (E14-04).
#
# Overlay: docker-compose.wis2box.yml (profile wis2box). Brings up the harness,
# probes MQTT + HTTP, optionally runs wis2* pytest (T3.4 fills publish cases).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${ROOT}/docker-compose.wis2box.yml"
COMPOSE=(docker compose -f "${ROOT}/docker-compose.yml" -f "${COMPOSE_FILE}")
HTTP_PORT="${WIS2BOX_HTTP_HOST_PORT:-9080}"
MQTT_PORT="${WIS2BOX_MQTT_HOST_PORT:-1883}"

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "[wis2box-harness] error — docker-compose.wis2box.yml missing." >&2
  exit 1
fi

if ! grep -Eq '^[[:space:]]*wis2box:[[:space:]]*$' "${COMPOSE_FILE}"; then
  echo "[wis2box-harness] error — no wis2box service in overlay (T3.3 regression)." >&2
  exit 1
fi

cd "${ROOT}"
echo "[wis2box-harness] bringing up profile wis2box…"
"${COMPOSE[@]}" --profile wis2box up -d --build --wait wis2box

cleanup() {
  # Stop only the harness service — do not `down` the whole compose project
  # (that would remove backend/frontend/db if they share the project name).
  "${COMPOSE[@]}" --profile wis2box stop wis2box || true
  "${COMPOSE[@]}" --profile wis2box rm -f wis2box || true
}
trap cleanup EXIT

probe() {
  local i
  for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:${HTTP_PORT}/health" >/dev/null \
      && (echo >"/dev/tcp/127.0.0.1/${MQTT_PORT}") 2>/dev/null; then
      echo "[wis2box-harness] ready — HTTP :${HTTP_PORT} + MQTT :${MQTT_PORT}"
      return 0
    fi
    sleep 1
  done
  echo "[wis2box-harness] error — harness did not become ready" >&2
  "${COMPOSE[@]}" --profile wis2box ps || true
  "${COMPOSE[@]}" --profile wis2box logs --no-color wis2box || true
  return 1
}

probe

# Smoke PUT/GET so T3.3 CI proves the HTTP dataset surface (MQTT port already probed).
SMOKE_URL="http://127.0.0.1:${HTTP_PORT}/datasets/ci-smoke.xml"
SMOKE_BODY='<ci>wis2box-harness</ci>'
curl -sf -X PUT -H 'Content-Type: application/xml' --data "${SMOKE_BODY}" "${SMOKE_URL}" >/dev/null
GOT="$(curl -sf "${SMOKE_URL}")"
if [[ "${GOT}" != "${SMOKE_BODY}" ]]; then
  echo "[wis2box-harness] error — dataset PUT/GET mismatch" >&2
  exit 1
fi
echo "[wis2box-harness] HTTP dataset PUT/GET smoke ok"

# Optional pytest path when TC-F17-001 tests exist (T3.4).
# Allowlist loopback/harness hosts for sink egress during those tests.
export DISSEMINATION_EGRESS_ALLOWLIST="${DISSEMINATION_EGRESS_ALLOWLIST:-wis2box,127.0.0.1,localhost}"

shopt -s nullglob
wis2_tests=(
  "${ROOT}"/packages/dissemination/tests/**/*wis2*
  "${ROOT}"/tests/**/*wis2*
)
# Unit tests under test_wis2_sink.py are mocked — only run files tagged for harness
# when T3.4 adds them. Prefer explicit *harness* / *staging* names if present.
harness_tests=()
for f in "${wis2_tests[@]}"; do
  case "$(basename "${f}")" in
    *harness*|*staging*|*compose*) harness_tests+=("${f}") ;;
  esac
done

if ((${#harness_tests[@]} > 0)); then
  uv run pytest "${harness_tests[@]}" \
    -m "not live and not live_api" \
    -v --no-cov
else
  echo "[wis2box-harness] compose profile wis2box green (publish pytest deferred to T3.4)."
fi
