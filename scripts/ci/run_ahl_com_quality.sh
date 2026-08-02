#!/usr/bin/env bash
# EV-029 / E29-T4 — AHL / COM / shared bulletin quality pack (M1).
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac2iwxxm: TC-EV029-003 AHL API + TC-F6-030 bulletin split"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_003_ahl_api.py \
  packages/tac2iwxxm/tests/test_tc_f6_030_bulletin_split.py \
  --no-cov -v --tb=short

echo "==> dissemination: EDIS AHL format (thin wrapper over tac2iwxxm)"
${UV} run pytest \
  packages/dissemination/tests/test_edis_format.py \
  --no-cov -v --tb=short

echo "==> ahl-com-quality pack green"
