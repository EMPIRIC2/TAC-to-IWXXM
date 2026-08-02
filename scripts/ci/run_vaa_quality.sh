#!/usr/bin/env bash
# EV-029 / E29-T4 — VAA quality pack (M9 / TC-EV029-005 + F26 deepen / #820).
# Separate per-family pack (FV / iwxxm:VolcanicAshAdvisory); complements VA SIGMET pack.
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac2iwxxm: TC-EV029-005 VAA gap fixtures + FV AHL BBB reportStatus"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_005_vaa_gap_fixtures.py \
  --no-cov -v --tb=short

echo "==> backend: convert-bulletin VAA AHL report_status (T9.2)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f6_030_convert_bulletin_unit.py \
  -k "vaa" \
  --no-cov -v --tb=short

echo "==> tac-validate: VAA accept/negative pack (F26 keep-green)"
${UV} run pytest packages/tac-validate/tests \
  -k "vaa or VAA" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: VAA convert / golden keyword pack (exclude VA SIGMET)"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "vaa or VolcanicAshAdvisory or (VAA and not va_sigmet and not VolcanicAshSIGMET)" \
  --no-cov -v --tb=short

echo "==> vaa-quality pack green"
