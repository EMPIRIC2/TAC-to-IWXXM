#!/usr/bin/env bash
# EV-035 — fast pre-commit canary (map exists + dig inventory smoke).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> EV-035 provenance canary"
test -f docs/domain/rules/PROVENANCE_MAP.json
test -f docs/domain/rules/PROVENANCE_MAP.md
${UV} run pytest \
  tests/provenance/test_tc_ev035_001_dig_inventory.py \
  tests/provenance/test_tc_ev035_006_gap_raise.py \
  -q --no-cov --tb=line

echo "==> EV-035 provenance canary green"
