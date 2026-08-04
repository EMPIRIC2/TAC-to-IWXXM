#!/usr/bin/env bash
# EV-032 / E32-T7 — fast pre-commit canary for #835 A6-2-TC (ADR-032 + catalog wmoPass).
# Path-filtered companion to make test-tc-sigmet-quality; do not dump full XSD+SCH here.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> EV-032 A6-2-TC canary (ev032_smoke)"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev032_002_a6_2_tc_adr032_equality.py \
  packages/tac2iwxxm/tests/test_tc_ev032_003_a6_2_tc_catalog_wmo_pass.py \
  -m ev032_smoke \
  --no-cov -q --tb=short

echo "==> EV-032 A6-2-TC canary green"
