#!/usr/bin/env bash
# dependency-cruiser — import-graph rules for JS/TS workspaces.
# Config: config/tooling/.dependency-cruiser.cjs. Report: .quality-reports/depcruise.{txt,json}.
# Usage: scripts/ci/run_depcruise.sh [extra depcruise args]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PNPM="${PNPM:-pnpm}"
REPORT_DIR="${QUALITY_REPORT_DIR:-.quality-reports}"
mkdir -p "${REPORT_DIR}"

TARGETS=(apps/frontend/src apps/e2e packages/shared/src packages/shared/tests packages/live-map-geometry/src packages/live-map-geometry/tests)
CONFIG=config/tooling/.dependency-cruiser.cjs

set +e
"${PNPM}" exec depcruise --config "${CONFIG}" --output-type err "$@" "${TARGETS[@]}" \
  2>&1 | tee "${REPORT_DIR}/depcruise.txt"
status=${PIPESTATUS[0]}
# Machine-readable graph/violations (best effort; exit code comes from the text run).
"${PNPM}" exec depcruise --config "${CONFIG}" --output-type json "$@" "${TARGETS[@]}" \
  >"${REPORT_DIR}/depcruise.json" 2>/dev/null
set -e

echo "depcruise exit=${status} report=${REPORT_DIR}/depcruise.txt"
exit "${status}"
