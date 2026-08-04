#!/usr/bin/env bash
# CI frontend audit gate. Treats retired npm audit API (HTTP 410) as skip, not fail.
# GHSA-mh99-v99m-4gvg / GHSA-rgw5-rvv9-x895: brace-expansion DoS advisories — pin via
# pnpm.overrides (1.1.18 / 2.1.2 / 5.0.9). Ignore listed IDs if audit still flags
# transitive minimatch@3 lines that cannot take 5.x.
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

# Ignored brace-expansion advisories when overrides pin maintenance lines (see package.json).
IGNORE_GHSA=(
  "GHSA-mh99-v99m-4gvg"
  "GHSA-rgw5-rvv9-x895"
)
GHSAS=()
while IFS= read -r id; do
  [[ -n "$id" ]] && GHSAS+=("$id")
done < <(printf '%s\n' "$OUTPUT" | grep -oE 'GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}' | sort -u || true)
OTHER=()
for id in "${GHSAS[@]+"${GHSAS[@]}"}"; do
  skip=0
  for ign in "${IGNORE_GHSA[@]}"; do
    if [[ "$id" == "$ign" ]]; then
      skip=1
      break
    fi
  done
  if [[ "$skip" -eq 0 ]]; then
    OTHER+=("$id")
  fi
done
if [[ ${#GHSAS[@]} -gt 0 && ${#OTHER[@]} -eq 0 ]]; then
  echo "WARN: ignoring brace-expansion GHSAs pinned via pnpm.overrides (${IGNORE_GHSA[*]})"
  exit 0
fi

exit "$CODE"
