#!/usr/bin/env bash
# F34 / EV-059 / #874 — pytest-gremlins mutation chunk (TC-F34-003 / TC-F34-005).
# Usage: scripts/ci/run_mutation_python.sh <target>
# Env:
#   GREMLIN_EXTRA_ARGS — extra pytest-gremlins flags (optional)
#   MUTATION_TIMEOUT_SEC — soft wall clock (default 1200); 0 disables
# Notes:
#   Nested package pyproject.toml files shift pytest rootdir; we force the workspace
#   root via --rootdir / -c so --gremlin-targets paths resolve correctly.
# Exclusions (Rust / e2e / generated xsdata): [tool.pytest-gremlins] in root pyproject.toml
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

TARGET="${1:-}"
if [[ -z "${TARGET}" ]]; then
  echo "Usage: $0 <target>" >&2
  echo "Targets: backend worker auth shared tac-validate tac2iwxxm iwxxm-validate dissemination poc-shared-env" >&2
  exit 2
fi

UV="${UV:-uv}"
TIMEOUT_SEC="${MUTATION_TIMEOUT_SEC:-1200}"
REPORT_DIR="${MUTATION_REPORT_DIR:-coverage/gremlins}"
mkdir -p "${REPORT_DIR}"

case "${TARGET}" in
  backend)
    GREMLIN_TARGETS="${ROOT}/apps/backend/src"
    PYTEST_PATHS=("${ROOT}/apps/backend/tests/unit")
    ;;
  worker)
    GREMLIN_TARGETS="${ROOT}/apps/worker/src/metar_worker"
    PYTEST_PATHS=("${ROOT}/apps/worker/tests")
    ;;
  auth)
    GREMLIN_TARGETS="${ROOT}/packages/auth/src/metar_auth"
    PYTEST_PATHS=("${ROOT}/tests/unit/auth")
    ;;
  shared)
    GREMLIN_TARGETS="${ROOT}/packages/shared/src/metar_shared"
    PYTEST_PATHS=("${ROOT}/packages/shared/tests")
    ;;
  tac-validate)
    GREMLIN_TARGETS="${ROOT}/packages/tac-validate/src/tac_validate"
    PYTEST_PATHS=("${ROOT}/packages/tac-validate/tests")
    ;;
  tac2iwxxm)
    GREMLIN_TARGETS="${ROOT}/packages/tac2iwxxm/src/tac2iwxxm"
    PYTEST_PATHS=("${ROOT}/packages/tac2iwxxm/tests")
    ;;
  iwxxm-validate)
    GREMLIN_TARGETS="${ROOT}/packages/iwxxm-validate/src/iwxxm_validate"
    PYTEST_PATHS=("${ROOT}/packages/iwxxm-validate/tests")
    ;;
  dissemination)
    GREMLIN_TARGETS="${ROOT}/packages/dissemination/src/dissemination"
    PYTEST_PATHS=("${ROOT}/packages/dissemination/tests")
    ;;
  poc-shared-env)
    GREMLIN_TARGETS="${ROOT}/packages/shared/src/metar_shared/env.py"
    PYTEST_PATHS=("${ROOT}/packages/shared/tests/test_shared_exports.py")
    ;;
  *)
    echo "Unknown mutation target: ${TARGET}" >&2
    exit 2
    ;;
esac

JSON_REPORT="${REPORT_DIR}/${TARGET}.json"
LOG_FILE="${REPORT_DIR}/${TARGET}.log"

CMD=(
  "${UV}" run pytest
  "${PYTEST_PATHS[@]}"
  --rootdir="${ROOT}"
  -c "${ROOT}/pyproject.toml"
  --gremlins
  --gremlin-targets="${GREMLIN_TARGETS}"
  --gremlin-report=console
  --gremlin-report=json
  --gremlins-html-dir="${REPORT_DIR}/${TARGET}-html"
  --override-ini=addopts=
  -m "not live and not live_api and not smoke and not integration"
  --tb=line
  -q
)
if [[ -n "${GREMLIN_EXTRA_ARGS:-}" ]]; then
  # shellcheck disable=SC2206
  EXTRA=( ${GREMLIN_EXTRA_ARGS} )
  CMD+=("${EXTRA[@]}")
fi

echo "mutation_python target=${TARGET} mutate=${GREMLIN_TARGETS} tests=${PYTEST_PATHS[*]} timeout_sec=${TIMEOUT_SEC}"

TIMEOUT_BIN=""
if [[ "${TIMEOUT_SEC}" != "0" ]]; then
  if command -v timeout >/dev/null 2>&1; then
    TIMEOUT_BIN="timeout"
  elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_BIN="gtimeout"
  else
    echo "WARN: no timeout(1)/gtimeout; running without wall-clock limit" >&2
  fi
fi

set +e
if [[ -n "${TIMEOUT_BIN}" ]]; then
  "${TIMEOUT_BIN}" --signal=TERM "${TIMEOUT_SEC}" "${CMD[@]}" 2>&1 | tee "${LOG_FILE}"
  rc=${PIPESTATUS[0]}
else
  "${CMD[@]}" 2>&1 | tee "${LOG_FILE}"
  rc=${PIPESTATUS[0]}
fi
set -e

if [[ -f coverage/gremlins/gremlins-report.json ]]; then
  cp coverage/gremlins/gremlins-report.json "${JSON_REPORT}" || true
fi

if [[ ${rc} -eq 124 ]]; then
  echo "mutation_python target=${TARGET} TIMED OUT after ${TIMEOUT_SEC}s (survivors may be incomplete)" >&2
  exit 0
fi

if [[ ${rc} -ne 0 ]]; then
  echo "mutation_python target=${TARGET} failed rc=${rc}" >&2
  exit "${rc}"
fi

echo "mutation_python target=${TARGET} OK"
exit 0
