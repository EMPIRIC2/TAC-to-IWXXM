#!/usr/bin/env bash
# Run deptry for every uv workspace member (config lives in each member's
# [tool.deptry] table).
# [Corpus: tech-spec]   docs/technical-requirements.md (dependency hygiene)
# [Corpus: system-spec] docs/architecture.md (component map)
#
# Reports: .quality-reports/deptry/<member>.txt  (+ summary.txt)
# Exit:    non-zero when any member reports DEP001-DEP004 findings.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

DEPTRY_VERSION="${DEPTRY_VERSION:-0.25.1}"
REPORT_DIR=".quality-reports/deptry"
mkdir -p "$REPORT_DIR"
: > "$REPORT_DIR/summary.txt"

MEMBERS=(
  packages/shared
  packages/auth
  packages/tac2iwxxm
  packages/tac-decoding
  packages/reference-lookup
  packages/iwxxm-validate
  packages/tac-validate
  packages/dissemination
  packages/workflows
  apps/backend
  apps/worker
)

if [[ -x "$ROOT/.venv/bin/deptry" ]]; then
  DEPTRY=("$ROOT/.venv/bin/deptry")
else
  DEPTRY=(uv run --no-sync --with "deptry==${DEPTRY_VERSION}" deptry)
fi

failed=0
for member in "${MEMBERS[@]}"; do
  report="$ROOT/$REPORT_DIR/${member//\//__}.txt"
  set +e
  (cd "$ROOT/$member" && "${DEPTRY[@]}" . --no-ansi) >"$report" 2>&1
  status=$?
  set -e
  if [[ $status -eq 0 ]]; then
    echo "PASS $member" | tee -a "$REPORT_DIR/summary.txt"
  else
    echo "FAIL $member (exit=$status) -> $REPORT_DIR/${member//\//__}.txt" | tee -a "$REPORT_DIR/summary.txt"
    failed=1
  fi
done

exit "$failed"
