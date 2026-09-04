#!/usr/bin/env bash
# EV-029 / E29-T4 — METAR quality pack (M2 / TC-EV029-007 + F15 deepen).
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

bash scripts/ci/ensure_iwxxm_validate_native.sh

echo "==> tac2iwxxm: TC-EV029-007 METAR gap fixtures + AHL BBB reportStatus"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_007_metar_gap_fixtures.py \
  --no-cov -v --tb=short

echo "==> tac-validate: METAR accept/negative keyword pack (F15 keep-green)"
${UV} run pytest packages/tac-validate/tests \
  -k "metar or METAR" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: METAR convert / golden keyword pack"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "metar or METAR" \
  --no-cov -v --tb=short

echo "==> metar-quality pack green"
