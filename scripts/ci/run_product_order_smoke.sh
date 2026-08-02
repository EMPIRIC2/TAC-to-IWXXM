#!/usr/bin/env bash
# EV-029 / T12.1 — Product-order regression smoke (TC-EV029-007 / M12).
# One accept fixture per family in Phase B order; complements per-family quality packs.
# Path-filtered companion workflow; does not replace ci.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> TC-EV029-007: product-order lint → convert → XSD+SCH (10 families)"
${UV} run pytest \
  packages/tac2iwxxm/tests/test_tc_ev029_007_product_order_smoke.py \
  --no-cov -v --tb=short

echo "==> product-order smoke green"
