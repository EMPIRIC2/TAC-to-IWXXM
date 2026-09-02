#!/usr/bin/env bash
# CI frontend audit gate. Treats retired npm audit API (HTTP 410) as skip, not fail.
# brace-expansion: pin via pnpm.overrides (1.1.18 / 2.1.4 / 5.0.9); ignore listed GHSAs
# if audit still flags transitive minimatch@3 lines.
# undici: jsdom@28 pins undici 7.28.x; bumping to 7.29.0 breaks wrap-handler path — ignore
# undici GHSAs until jsdom ships a compatible peer (dev/test-only surface).
# stryker: @stryker-mutator/* → ajv/fast-uri + typed-rest-client/qs — mutation/dev-only;
# ignore until upstream bumps (EV-097 push unblock 2026-09-02).
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

IGNORE_GHSA=(
  "GHSA-mh99-v99m-4gvg"
  "GHSA-rgw5-rvv9-x895"
  "GHSA-4cwx-7wf7-3272"
  "GHSA-8xcm-r25x-g524"
  "GHSA-m8rv-5g2x-5cg5"
  "GHSA-jr45-8vmc-qm54"
  "GHSA-v3r7-h72x-cjcm"
  "GHSA-4mjr-xmp4-gh2g"
  "GHSA-5jgf-p345-68v8"
  "GHSA-f65p-4m7j-42xc"
  "GHSA-fph4-wmhf-6fwf"
  "GHSA-jqff-g426-hqxp"
  "GHSA-x5fp-wj9c-mxmx"
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
  echo "WARN: ignoring brace-expansion/undici GHSAs pinned or waived (${IGNORE_GHSA[*]})"
  exit 0
fi

if [[ ${#OTHER[@]} -gt 0 ]]; then
  echo "ERROR: unignored advisories: ${OTHER[*]}"
fi

exit "$CODE"
