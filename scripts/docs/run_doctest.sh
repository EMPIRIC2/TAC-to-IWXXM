#!/usr/bin/env bash
# Run doctests per package tree to avoid module basename clashes.
# [Corpus: adr/ADR-048]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

run_one() {
  local label="$1"
  shift
  echo "== test-doctest: ${label} =="
  # Warnings as errors for this gate (D-EVDOC-05 / TC-EVDOC-004)
  uv run python -W error -m pytest -o addopts= \
    -o asyncio_default_fixture_loop_scope=function \
    --doctest-modules "$@" \
    --ignore-glob='**/tests/**' \
    --ignore-glob='**/iwxxm_xsd/**' \
    --ignore-glob='**/generated/**' \
    --ignore-glob='**/testing/**' \
    --ignore-glob='**/scripts/**' \
    -q --tb=line
}

# Packages with unique import roots (one tree at a time)
run_one tac-decoding packages/tac-decoding/src
run_one tac-validate packages/tac-validate/src
run_one iwxxm-validate packages/iwxxm-validate/src
run_one dissemination packages/dissemination/src
run_one workflows packages/workflows/src
run_one auth packages/auth/src
run_one shared packages/shared
# tac2iwxxm after tac-decoding so shims resolve correctly when isolated
run_one tac2iwxxm packages/tac2iwxxm/src \
  --ignore=packages/tac2iwxxm/src/tac2iwxxm/decode.py \
  --ignore=packages/tac2iwxxm/src/tac2iwxxm/glossary.py
run_one backend apps/backend/src
run_one worker apps/worker

echo "test-doctest: all package trees OK"
