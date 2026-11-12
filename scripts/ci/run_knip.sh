#!/usr/bin/env bash
# Knip — unused files / exports / dependencies for JS/TS workspaces.
# Config: config/tooling/knip.json. Report: .quality-reports/knip.{txt,json}.
# Usage: scripts/ci/run_knip.sh [extra knip args]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PNPM="${PNPM:-pnpm}"
REPORT_DIR="${QUALITY_REPORT_DIR:-.quality-reports}"
mkdir -p "${REPORT_DIR}"

set +e
"${PNPM}" exec knip --config config/tooling/knip.json --no-progress "$@" \
  2>&1 | tee "${REPORT_DIR}/knip.txt"
status=${PIPESTATUS[0]}
# Machine-readable report (best effort; exit code comes from the text run).
"${PNPM}" exec knip --config config/tooling/knip.json --no-progress \
  --reporter json "$@" >"${REPORT_DIR}/knip.json" 2>/dev/null
set -e

echo "knip exit=${status} report=${REPORT_DIR}/knip.txt"
exit "${status}"
