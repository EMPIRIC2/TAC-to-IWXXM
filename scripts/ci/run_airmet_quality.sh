#!/usr/bin/env bash
# EV-029 / E29-T4 — AIRMET quality pack (M8 / TC-EV029-007 + F24 deepen).
# Separate per-family pack (WA / iwxxm:AIRMET); complements SIGMET-family packs.
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac2iwxxm: TC-EV029-007 AIRMET gap fixtures + WA AHL BBB reportStatus"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_007_airmet_gap_fixtures.py \
  --no-cov -v --tb=short

echo "==> backend: convert-bulletin AIRMET AHL report_status (T8.2)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f6_030_convert_bulletin_unit.py \
  -k "airmet" \
  --no-cov -v --tb=short

echo "==> tac-validate: AIRMET accept/negative pack (F24 keep-green)"
${UV} run pytest packages/tac-validate/tests \
  -k "airmet" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: AIRMET convert / golden keyword pack (exclude incidental TAF/SIGMET US)"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "airmet and not taf_us and not sigmet_us" \
  --no-cov -v --tb=short

echo "==> airmet-quality pack green"
