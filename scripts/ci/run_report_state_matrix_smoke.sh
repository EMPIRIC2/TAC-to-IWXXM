#!/usr/bin/env bash
# EV-029 / T12.2 — Report-state matrix smoke (TC-EV029-006 / M12).
# BBB→reportStatus + CNL/NIL product paths; complements per-family quality packs.
# Path-filtered companion workflow; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> TC-EV029-006: report-state matrix (BBB / CNL / NIL)"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_006_report_state_matrix.py \
  --no-cov -v --tb=short

echo "==> report-state matrix smoke green"
