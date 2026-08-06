#!/usr/bin/env bash
# S046 / EV-038 / #853 — iwxxm-us compatibility gate smoke (TC-EV038-006).
# Path-filtered companion workflow; does not replace ci-cd.yml.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> TC-EV038-006: iwxxm-us compat gate (D-S046-853 Ship WMO-only first)"
${UV} run python scripts/iwxxm/iwxxm_us_compat_gate.py --smoke

echo "==> iwxxm-us compat smoke green"
