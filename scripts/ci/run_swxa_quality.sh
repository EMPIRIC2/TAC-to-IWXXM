#!/usr/bin/env bash
# EV-029 / E29-T4 — SWXA quality pack (M11 / TC-F28 + F28 deepen / #740/#823).
# Separate per-family pack (FN / iwxxm:SpaceWeatherAdvisory); complements AHL COM pack.
# Path-filtered companion to per-family workflows; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac-validate: SWXA SX1 registry + accept/negative (TC-F28-001/004)"
${UV} run pytest \
  packages/tac-validate/tests/test_tc_f28_001_registry_completeness.py \
  packages/tac-validate/tests/test_tc_f28_sx1_swxa.py \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: SWXA convert / golden / adjacency (TC-F28-002/003/006)"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_f28_002_003_swxa_annex3.py \
  packages/tac2iwxxm/tests/test_tc_f28_006_swxa_adjacency.py \
  packages/tac2iwxxm/tests/test_tc_ev029_003_ahl_api.py \
  -k "swxa or SWXA or fn_swxa or SpaceWeather" \
  --no-cov -v --tb=short

echo "==> backend: product=swxa runtime enum (T11.5 / S02.M1)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f28_swxa_product_enum.py \
  --no-cov -v --tb=short

echo "==> swxa-quality pack green"
