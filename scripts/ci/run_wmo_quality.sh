#!/usr/bin/env bash
# F24/F25 / EV-020 — combined WMO quality pack (E20-F3=3).
# Runs path- and keyword-filtered pytest for SIGMET (keep green) + AIRMET +
# METAR/SPECI/TAF WMO-related tests in tac-validate + tac2iwxxm.
# Does not replace full package coverage jobs in ci-cd.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac-validate: SIGMET / AIRMET fixtures + lint coverage"
${UV} run pytest packages/tac-validate/tests \
  -k "sigmet or SIGMET or airmet or AIRMET or VolcanicAsh" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: SIGMET / AIRMET / METAR / SPECI / TAF convert + decode"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "sigmet or SIGMET or airmet or AIRMET or VolcanicAsh or metar or METAR or speci or SPECI or taf or TAF" \
  --no-cov -v --tb=short

echo "==> wmo-quality pack green"
