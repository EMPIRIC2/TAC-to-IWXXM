#!/usr/bin/env bash
# EV-035 / S043 — provenance quality pack (TC-EV035-001..006).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> EV-035 provenance quality (TC-EV035-001..006)"
${UV} run pytest tests/provenance/ -q --no-cov --tb=short

echo "==> EV-035 provenance quality green"
