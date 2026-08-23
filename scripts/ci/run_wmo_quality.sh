#!/usr/bin/env bash
# F26/F27 / EV-021 — combined WMO quality pack (extends E20-F3 / S02.L1).
# Runs path- and keyword-filtered pytest for SIGMET (keep green) + AIRMET +
# METAR/SPECI/TAF + VAA + TCA WMO-related tests in tac-validate + tac2iwxxm.
# Does not replace full package coverage jobs in ci-cd.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

bash scripts/ci/ensure_iwxxm_validate_native.sh

# Keep F23–F25 green while growing VAA/TCA (S027). "VolcanicAsh" covers VA SIGMET;
# "vaa" / "VAA" / "va_advisory" / "va-advisory" cover VAA; same pattern for TCA.
TV_K='sigmet or SIGMET or airmet or AIRMET or VolcanicAsh or vaa or VAA or va_advisory or va-advisory or tca or TCA or TropicalCyclone or tc_advisory or tc-advisory'
T2_K="${TV_K} or metar or METAR or speci or SPECI or taf or TAF"

echo "==> tac-validate: SIGMET / AIRMET / VAA / TCA fixtures + lint coverage"
${UV} run pytest packages/tac-validate/tests \
  -k "${TV_K}" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: SIGMET / AIRMET / METAR / SPECI / TAF / VAA / TCA convert + decode"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "${T2_K}" \
  --no-cov -v --tb=short

echo "==> wmo-quality pack green"
