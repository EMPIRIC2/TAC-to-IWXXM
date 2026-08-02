#!/usr/bin/env bash
# EV-029 / E29-T4 — SPECI quality pack (M3 / TC-EV029-007 + F20 deepen).
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac2iwxxm: TC-EV029-007 SPECI gap fixtures + AHL BBB reportStatus"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_007_speci_gap_fixtures.py \
  --no-cov -v --tb=short

echo "==> backend: convert-bulletin SPECI AHL report_status (T3.2)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f6_030_convert_bulletin_unit.py \
  -k "speci" \
  --no-cov -v --tb=short

echo "==> tac-validate: SPECI accept/negative keyword pack (F20 keep-green)"
${UV} run pytest packages/tac-validate/tests \
  -k "speci or SPECI" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: SPECI convert / golden keyword pack"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "speci or SPECI" \
  --no-cov -v --tb=short

echo "==> speci-quality pack green"
