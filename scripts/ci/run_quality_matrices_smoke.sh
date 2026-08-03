#!/usr/bin/env bash
# EV-030 / E30-T7 / TC-F29-006 — F29 quality-matrix PR smoke.
# Inventory gate + loaders/runners + structural pilot checks + ready slots only.
# Excludes @pytest.mark.quality_matrix (full 95×20 slot expansion).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> F29 quality matrices: PR smoke (not quality_matrix)"
${UV} run pytest tests/quality_matrices \
  -m "not quality_matrix" \
  --no-cov -v --tb=short

echo "==> quality-matrices smoke green"
