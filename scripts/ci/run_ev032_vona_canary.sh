#!/usr/bin/env bash
# EV-032 / E32-T7 / T2.8 — fast pre-commit canary for F32 VONA (ADR-032 + product enum).
# Path-filtered companion to make test-vona-quality; do not dump full XSD+SCH here.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> EV-032 VONA canary (ev032_smoke)"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_f32_004_vona_validate_golden.py \
  apps/backend/tests/unit/test_tc_f32_vona_product_enum.py \
  -m ev032_smoke \
  --no-cov -q --tb=short

echo "==> EV-032 VONA canary green"
