#!/usr/bin/env bash
# EV-029 / E29-T4 — TC SIGMET quality pack (M7 / TC-EV029-004 + F23 deepen / #738).
# EV-032 / E32-T7 / T1.5 — also runs #835 A6-2-TC ADR-032 equality + catalog wmoPass.
# Separate per-family pack (WC / TropicalCycloneSIGMET); complements gen + VA packs.
# Path-filtered companion to per-family workflows; does not replace ci.yml.
# Note: no dedicated tac-validate F23 TC registry pack yet — lint coverage is via
# gap-fixture product-order (lint → convert → validate).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> EV-032 / #835: A6-2-TC ADR-032 equality + catalog wmoPass (long pack)"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev032_002_a6_2_tc_adr032_equality.py \
  packages/tac2iwxxm/tests/test_tc_ev032_003_a6_2_tc_catalog_wmo_pass.py \
  packages/tac2iwxxm/tests/test_tc_ev030_005_sigmet_a6_2_tc_catalog.py \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: TC-EV029-004/007 TC SIGMET gap fixtures + WC AHL BBB reportStatus"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_007_tc_sigmet_gap_fixtures.py \
  --no-cov -v --tb=short

echo "==> backend: convert-bulletin TC SIGMET AHL report_status (T7.2)"
${UV} run pytest \
  apps/backend/tests/unit/test_tc_f6_030_convert_bulletin_unit.py \
  -k "tc_sigmet" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: TC SIGMET convert / AHL keyword pack (exclude TCA advisory suite)"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "tc_sigmet" \
  --no-cov -v --tb=short

echo "==> tc-sigmet-quality pack green"
