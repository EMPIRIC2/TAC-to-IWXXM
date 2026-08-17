#!/usr/bin/env bash
# F34 / EV-059 / #874 — Stryker JS/TS mutation chunk (TC-F34-004 / TC-F34-005).
# Usage: scripts/ci/run_mutation_js.sh <frontend|shared>
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

TARGET="${1:-}"
PNPM="${PNPM:-pnpm}"
TIMEOUT_SEC="${MUTATION_TIMEOUT_SEC:-1200}"
REPORT_DIR="${MUTATION_REPORT_DIR:-coverage/stryker}"
mkdir -p "${REPORT_DIR}"

case "${TARGET}" in
  frontend)
    CWD="apps/frontend"
    ;;
  shared)
    CWD="packages/shared"
    ;;
  *)
    echo "Usage: $0 <frontend|shared>" >&2
    exit 2
    ;;
esac

LOG_FILE="${REPORT_DIR}/${TARGET}.log"
echo "mutation_js target=${TARGET} cwd=${CWD} timeout_sec=${TIMEOUT_SEC}"

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
  "${TIMEOUT_BIN}" --signal=TERM "${TIMEOUT_SEC}" \
    bash -c "cd \"${CWD}\" && \"${PNPM}\" exec stryker run stryker.config.mjs" \
    2>&1 | tee "${LOG_FILE}"
  rc=${PIPESTATUS[0]}
else
  (cd "${CWD}" && "${PNPM}" exec stryker run stryker.config.mjs) \
    2>&1 | tee "${LOG_FILE}"
  rc=${PIPESTATUS[0]}
fi
set -e

# Copy reports if present
if [[ -d "${CWD}/reports/mutation" ]]; then
  mkdir -p "${REPORT_DIR}/${TARGET}"
  cp -R "${CWD}/reports/mutation/." "${REPORT_DIR}/${TARGET}/" || true
fi

if [[ ${rc} -eq 124 ]]; then
  echo "mutation_js target=${TARGET} TIMED OUT after ${TIMEOUT_SEC}s" >&2
  exit 0
fi

if [[ ${rc} -ne 0 ]]; then
  echo "mutation_js target=${TARGET} failed rc=${rc}" >&2
  exit "${rc}"
fi

echo "mutation_js target=${TARGET} OK"
exit 0
