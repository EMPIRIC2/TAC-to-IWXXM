#!/usr/bin/env bash
# S019 / EV-014 T0.1 — coverage gate for packages/dissemination (F16–F19).
#
# Until T1.1/T1.2 scaffold the package, this script exits 0 with a skip notice
# so CI matrix / Makefile targets can land in 06-tech-tooling without failing.
# When the package exists, enforce 95% branch coverage (sibling package bar;
# ADR-007 universal ≥95%).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PKG="${ROOT}/packages/dissemination"
PYPROJECT="${PKG}/pyproject.toml"

if [[ ! -f "${PYPROJECT}" ]]; then
  echo "[dissemination-coverage] skip — packages/dissemination not scaffolded yet (execution plan T1.1/T1.2)."
  exit 0
fi

cd "${ROOT}"
# Unit coverage gate: exclude Testcontainers engine suite (T2.5) from the 95% path;
# those tests are invoked via `make test-integration-dissemination` (Docker optional).
uv run pytest packages/dissemination/tests \
  -m "not integration" \
  --cov=dissemination \
  --cov-config=packages/dissemination/pyproject.toml \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=json:packages/dissemination/coverage.json \
  --cov-fail-under=100 \
  -v
exec uv run python scripts/ci/check_per_file_coverage.py \
  packages/dissemination/coverage.json
