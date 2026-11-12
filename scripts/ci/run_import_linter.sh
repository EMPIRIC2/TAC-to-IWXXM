#!/usr/bin/env bash
# Run Import Linter against the monorepo layering contracts.
# [Corpus: system-spec] docs/architecture.md (package boundaries)
# [Corpus: tech-spec]   docs/technical-requirements.md (quality gates)
#
# Contracts: config/tooling/importlinter.ini
# Report:    .quality-reports/import-linter.txt
#
# Uses the workspace venv's `lint-imports` when installed (root dev group);
# otherwise falls back to an ephemeral `uv run --with` so the gate works before
# the dependency lands in uv.lock.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

IMPORT_LINTER_VERSION="${IMPORT_LINTER_VERSION:-2.16}"
CONFIG="config/tooling/importlinter.ini"
REPORT_DIR=".quality-reports"
REPORT="$REPORT_DIR/import-linter.txt"
mkdir -p "$REPORT_DIR"

if [[ -x .venv/bin/lint-imports ]]; then
  LINT=(.venv/bin/lint-imports)
else
  LINT=(uv run --no-sync --with "import-linter==${IMPORT_LINTER_VERSION}" lint-imports)
fi

set +e
"${LINT[@]}" --config "$CONFIG" 2>&1 | tee "$REPORT"
status=${PIPESTATUS[0]}
set -e

echo "import-linter exit=$status report=$REPORT"
exit "$status"
