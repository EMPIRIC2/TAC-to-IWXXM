#!/usr/bin/env bash
# EV-032 / E32-T7 / T2.8 — VONA quality pack (M2 / TC-F32 + F32 deepen / #741).
# Long pack: lint → convert → XSD+SCH/ADR-032 + API enum smoke.
# Fast canary: scripts/ci/run_ev032_vona_canary.sh (path-filtered pre-commit).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac-validate: VONA V1 registry + accept/negative (TC-F32-001)"
${UV} run pytest \
  packages/tac-validate/tests/test_tc_f32_v1_vona.py \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: VONA convert / golden / XSD+SCH (TC-F32-002/003/004)"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_f32_002_003_vona_annex3.py \
  packages/tac2iwxxm/tests/test_tc_f32_004_vona_validate_golden.py \
  packages/tac2iwxxm/tests/test_vona_coverage_helpers.py \
  --no-cov -v --tb=short

echo "==> backend: product=vona runtime enum + smoke (TC-F32-005/006)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f32_vona_product_enum.py \
  apps/backend/tests/integration/test_tc_f32_005_vona_smoke.py \
  --no-cov -v --tb=short

echo "==> vona-quality pack green"
