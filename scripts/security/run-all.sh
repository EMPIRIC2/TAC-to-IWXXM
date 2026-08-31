#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CANDIDATES=(
  "${HOME}/.cursor/skills/support/security-static-analysis/scripts/run-all.sh"
  "${HOME}/.cursor/skills/security-static-analysis/scripts/run-all.sh"
)
export SEC_SKIP_SUPABASE_ADVISORS="${SEC_SKIP_SUPABASE_ADVISORS:-1}"
for s in "${CANDIDATES[@]}"; do
  [[ -f "$s" ]] && exec bash "$s" "$ROOT"
done
echo "missing security-static-analysis runner" >&2; exit 1
