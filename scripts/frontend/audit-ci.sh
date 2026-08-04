#!/usr/bin/env bash
# CI frontend audit gate. Treats retired npm audit API (HTTP 410) as skip, not fail.
# GHSA-mh99-v99m-4gvg / GHSA-rgw5-rvv9-x895 list brace-expansion ranges that conflict
# with eslint's minimatch@3 when forced to 5.x only. We pin maintenance lines
# (1.1.18 / 2.1.4 / 5.0.9) via pnpm.overrides; ignore remaining brace-expansion
# advisories on the 1.x eslint path until eslint drops minimatch@3.
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

# Allowed brace-expansion advisories after pnpm.overrides pins (see header).
# Portable for macOS /bin/bash 3.2 (no mapfile).
ALLOWED_BRACE=(
  "GHSA-mh99-v99m-4gvg"
  "GHSA-rgw5-rvv9-x895"
)
GHSAS=()
while IFS= read -r id; do
  [[ -n "$id" ]] && GHSAS+=("$id")
done < <(printf '%s\n' "$OUTPUT" | grep -oE 'GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}' | sort -u || true)
OTHER=()
for id in "${GHSAS[@]+"${GHSAS[@]}"}"; do
  keep=1
  for allowed in "${ALLOWED_BRACE[@]}"; do
    if [[ "$id" == "$allowed" ]]; then
      keep=0
      break
    fi
  done
  if [[ "$keep" -eq 1 ]]; then
    OTHER+=("$id")
  fi
done
if [[ ${#GHSAS[@]} -gt 0 && ${#OTHER[@]} -eq 0 ]]; then
  echo "WARN: ignoring brace-expansion GHSAs (pinned via pnpm.overrides; 5.x-only breaks eslint/minimatch@3)"
  exit 0
fi

exit "$CODE"
