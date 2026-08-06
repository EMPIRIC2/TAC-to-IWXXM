#!/usr/bin/env bash
# S046 / EV-038 / #859 — codes.wmo.int SCH↔CSV URI drift (TC-EV038-008).
# Offline only in CI (non-flake). Use --live locally for advisory live RDF.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

echo "==> TC-EV038-008: codes.wmo.int URI drift (D-S046-859)"
${UV} run python scripts/iwxxm/codelist_uri_drift.py

echo "==> codelist URI drift green"
