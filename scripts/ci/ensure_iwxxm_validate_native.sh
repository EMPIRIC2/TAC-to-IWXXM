#!/usr/bin/env bash
# Ensure iwxxm-validate PyO3 is built for CA_ECCC 3.0.0 XSD (xmloxide + catalog roots).
# EV-068: quality packs and tac2iwxxm jobs call validate() on ca_eccc goldens; without
# native extension, Python/lxml hits SCHEMA_PARSE_ERROR on GML imports.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

UV="${UV:-uv}"

if "${UV}" run python -c "from iwxxm_validate import rust_available; import sys; sys.exit(0 if rust_available() else 1)" 2>/dev/null; then
  echo "==> iwxxm-validate native extension already available"
  exit 0
fi

if ! command -v rustc >/dev/null 2>&1; then
  echo "::error::rustc required to build iwxxm-validate native extension (install Rust toolchain)"
  exit 1
fi

echo "==> Building iwxxm-validate native extension (CA_ECCC XSD gate)"
"${UV}" pip install maturin
(
  cd packages/iwxxm-validate
  source "${HOME}/.cargo/env" 2>/dev/null || true
  "${UV}" run maturin develop --manifest-path rust/Cargo.toml --uv
)

"${UV}" run python -c "from iwxxm_validate import rust_available; assert rust_available()"
