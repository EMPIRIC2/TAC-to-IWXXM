#!/usr/bin/env bash
# CI frontend audit gate. Treats retired npm audit API (HTTP 410) as skip, not fail.
# GHSA-mh99-v99m-4gvg lists brace-expansion "<=5.0.7" with patch only 5.0.8, which
# breaks minimatch@3 (eslint). We pin maintenance lines (1.1.16 / 2.1.2 / 5.0.8) via
# pnpm.overrides; ignore this advisory until eslint drops minimatch@3.
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

# Sole remaining GHSA is brace-expansion advisory (see header comment).
# Portable for macOS /bin/bash 3.2 (no mapfile).
GHSAS=()
while IFS= read -r id; do
  [[ -n "$id" ]] && GHSAS+=("$id")
done < <(printf '%s\n' "$OUTPUT" | grep -oE 'GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}' | sort -u || true)
OTHER=()
for id in "${GHSAS[@]+"${GHSAS[@]}"}"; do
  if [[ "$id" != "GHSA-mh99-v99m-4gvg" ]]; then
    OTHER+=("$id")
  fi
done
if [[ ${#GHSAS[@]} -gt 0 && ${#OTHER[@]} -eq 0 ]]; then
  echo "WARN: ignoring GHSA-mh99-v99m-4gvg (brace-expansion; pinned via pnpm.overrides; 5.0.8 breaks eslint/minimatch@3)"
  exit 0
fi

exit "$CODE"
