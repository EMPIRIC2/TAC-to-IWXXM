#!/usr/bin/env bash
set -euo pipefail
CANDIDATES=(
  "${HOME}/.cursor/skills/support/security-static-analysis/scripts/install-tools.sh"
  "${HOME}/.cursor/skills/security-static-analysis/scripts/install-tools.sh"
)
for s in "${CANDIDATES[@]}"; do
  [[ -f "$s" ]] && exec bash "$s"
done
echo "missing security-static-analysis installer" >&2; exit 1
