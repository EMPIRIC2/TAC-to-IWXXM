#!/usr/bin/env bash
# EV-029 / E29-T4 — TAF quality pack (M4 / TC-EV029-007 + F20 deepen).
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac2iwxxm: TC-EV029-007 TAF gap fixtures + AHL BBB reportStatus"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_007_taf_gap_fixtures.py \
  --no-cov -v --tb=short

echo "==> backend: convert-bulletin TAF AHL report_status (T4.2)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f6_030_convert_bulletin_unit.py \
  -k "taf" \
  --no-cov -v --tb=short

echo "==> tac-validate: TAF accept/negative keyword pack (F20 keep-green)"
${UV} run pytest packages/tac-validate/tests \
  -k "taf or TAF" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: TAF convert / golden keyword pack"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "taf or TAF" \
  --no-cov -v --tb=short

echo "==> taf-quality pack green"
