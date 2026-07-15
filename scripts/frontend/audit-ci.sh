#!/usr/bin/env bash
# CI frontend audit gate. Treats retired npm audit API (HTTP 410) as skip, not fail.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/frontend"

set +e
OUTPUT="$(pnpm audit --audit-level=low 2>&1)"
CODE=$?
set -e

printf '%s\n' "$OUTPUT"

if [[ "$CODE" -eq 0 ]]; then
  exit 0
fi

if printf '%s\n' "$OUTPUT" | grep -Eqi '410|ERR_PNPM_AUDIT_BAD_RESPONSE|endpoint.*retired|bulk advisory'; then
  echo "WARN: npm/pnpm audit endpoint unavailable (treating as skip; not a vulnerability fail)"
  exit 0
fi

exit "$CODE"
