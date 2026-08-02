#!/usr/bin/env bash
# EV-029 / E29-T4 — general SIGMET quality pack (M5 / TC-EV029-007 + F23 deepen).
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac2iwxxm: TC-EV029-007 gen SIGMET gap fixtures + AHL BBB reportStatus"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_007_sigmet_gap_fixtures.py \
  --no-cov -v --tb=short

echo "==> backend: convert-bulletin SIGMET AHL report_status (T5.2)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f6_030_convert_bulletin_unit.py \
  -k "sigmet" \
  --no-cov -v --tb=short

echo "==> tac-validate: SIGMET accept/negative keyword pack (F23 keep-green)"
${UV} run pytest packages/tac-validate/tests \
  -k "sigmet or SIGMET" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: SIGMET convert / golden keyword pack"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "sigmet or SIGMET" \
  --no-cov -v --tb=short

echo "==> sigmet-quality pack green"
