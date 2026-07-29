#!/usr/bin/env bash
# F23 / EV-019 — focused SIGMET + VA SIGMET quality pack (E19-19).
# Runs path- and keyword-filtered pytest for tac-validate + tac2iwxxm.
# Does not replace full package coverage jobs in ci-cd.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> tac-validate: SIGMET fixtures + template/gate + lint product coverage"
${UV} run pytest packages/tac-validate/tests \
  -k "sigmet or SIGMET" \
  --no-cov -v --tb=short

echo "==> tac2iwxxm: SIGMET / VA convert + decode + product matrix"
${UV} run pytest packages/tac2iwxxm/tests \
  -k "sigmet or SIGMET or VolcanicAsh" \
  --no-cov -v --tb=short

echo "==> sigmet-quality pack green"
