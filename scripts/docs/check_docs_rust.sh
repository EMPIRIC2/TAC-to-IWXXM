#!/usr/bin/env bash
# ADR-048 Rust documentation gate.
# Prefer: missing_docs deny + cargo test --doc (pure-Rust examples, no Python).
# [Corpus: adr/ADR-048]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Pin PyO3 to the workspace interpreter (host 3.14+ otherwise fails pyo3-ffi build).
if command -v uv >/dev/null 2>&1; then
  export PYO3_PYTHON="$(uv run python -c 'import sys; print(sys.executable)')"
fi

CRATES=(
  packages/tac2iwxxm/rust
  packages/iwxxm-validate/rust
)

fail=0
for crate in "${CRATES[@]}"; do
  echo "== check-docs-rust: ${crate} =="
  if [[ ! -f "${crate}/Cargo.toml" ]]; then
    echo "missing Cargo.toml: ${crate}" >&2
    fail=1
    continue
  fi
  # Document with warnings as errors for missing_docs when crate enables it;
  # always run doctests.
  if ! (cd "${crate}" && cargo doc --no-deps 2>&1); then
    echo "cargo doc failed: ${crate}" >&2
    fail=1
  fi
  if ! (cd "${crate}" && cargo test --doc --no-default-features 2>&1); then
    echo "cargo test --doc failed: ${crate}" >&2
    fail=1
  fi
done

exit "${fail}"
