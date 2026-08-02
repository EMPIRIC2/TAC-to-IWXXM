#!/usr/bin/env bash
# EV-029 / E29-T4 — VA SIGMET quality pack (M6 / TC-EV029-007 + F23 deepen).
# Separate per-family pack (WV / VolcanicAshSIGMET); complements gen sigmet-quality.
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac2iwxxm: TC-EV029-007 VA SIGMET gap fixtures + WV AHL BBB reportStatus"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_007_va_sigmet_gap_fixtures.py \
  --no-cov -v --tb=short

echo "==> backend: convert-bulletin VA SIGMET AHL report_status (T6.2)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f6_030_convert_bulletin_unit.py \
  -k "va_sigmet" \
  --no-cov -v --tb=short

echo "==> tac-validate: VA SIGMET accept/negative pack (F23 keep-green; exclude VAA)"
${UV} run pytest packages/tac-validate/tests \
  -k "va_sigmet or (sigmet and va and not vaa and not VAA)" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: VA SIGMET convert / golden keyword pack (exclude VAA)"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "va_sigmet or VolcanicAshSIGMET or (sigmet and va and not vaa and not VAA and not VolcanicAshAdvisory)" \
  --no-cov -v --tb=short

echo "==> va-sigmet-quality pack green"
