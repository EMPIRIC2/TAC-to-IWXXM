#!/usr/bin/env bash
# S019 / EV-014 T0.1 — CI Compose hook for F17 wis2box harness (E14-04).
#
# Overlay: docker-compose.wis2box.yml (profile wis2box). Real service lands in T3.3.
# Until a `wis2box` service is defined, exit 0 with skip so the hook can ship in 06.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${ROOT}/docker-compose.wis2box.yml"
COMPOSE=(docker compose -f "${ROOT}/docker-compose.yml" -f "${COMPOSE_FILE}")

if [[ ! -f "${COMPOSE_FILE}" ]]; then
  echo "[wis2box-harness] skip — docker-compose.wis2box.yml missing."
  exit 0
fi

if ! grep -Eq '^[[:space:]]*wis2box:[[:space:]]*$' "${COMPOSE_FILE}"; then
  echo "[wis2box-harness] skip — no wis2box service yet (execution plan T3.3)."
  exit 0
fi

cd "${ROOT}"
echo "[wis2box-harness] bringing up profile wis2box…"
"${COMPOSE[@]}" --profile wis2box up -d --wait wis2box

cleanup() {
  "${COMPOSE[@]}" --profile wis2box down --remove-orphans || true
}
trap cleanup EXIT

# Optional pytest path when TC-F17-001 tests exist (T3.4).
shopt -s nullglob
wis2_tests=(
  "${ROOT}"/packages/dissemination/tests/**/*wis2*
  "${ROOT}"/tests/**/*wis2*
)
if ((${#wis2_tests[@]} > 0)); then
  uv run pytest "${wis2_tests[@]}" \
    -m "not live and not live_api" \
    -v --no-cov
else
  echo "[wis2box-harness] compose profile wis2box is up (no wis2* tests found yet — T3.4)."
fi
