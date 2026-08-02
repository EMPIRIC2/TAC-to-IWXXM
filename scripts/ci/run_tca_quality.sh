#!/usr/bin/env bash
# EV-029 / E29-T4 — TCA quality pack (M10 / TC-EV029-005 + F27 deepen / #820).
# Separate per-family pack (FK / iwxxm:TropicalCycloneAdvisory); complements TC SIGMET pack.
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac2iwxxm: TC-EV029-005 TCA gap fixtures + FK AHL BBB reportStatus"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_005_tca_gap_fixtures.py \
  --no-cov -v --tb=short

echo "==> backend: convert-bulletin TCA AHL report_status (T10.2)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f6_030_convert_bulletin_unit.py \
  -k "tca" \
  --no-cov -v --tb=short

echo "==> tac-validate: TCA accept/negative pack (F27 keep-green)"
${UV} run pytest packages/tac-validate/tests \
  -k "tca or TCA" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: TCA convert / golden keyword pack (exclude TC SIGMET)"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "tca or TropicalCycloneAdvisory or (TCA and not tc_sigmet and not TropicalCycloneSIGMET)" \
  --no-cov -v --tb=short

echo "==> tca-quality pack green"
