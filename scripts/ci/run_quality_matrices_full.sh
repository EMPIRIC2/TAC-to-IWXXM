#!/usr/bin/env bash
# EV-030 / E30-T7 / TC-F29-006 — F29 full quality-matrix suite (optional / on-demand).
# Includes parametrized lint/convert/validate slots (needs-fixture/oos skip).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> F29 quality matrices: full pilot suite"
${UV} run pytest tests/quality_matrices \
  --no-cov -v --tb=short

echo "==> quality-matrices full green"
