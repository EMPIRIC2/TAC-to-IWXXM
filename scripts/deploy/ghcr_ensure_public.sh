#!/usr/bin/env bash
# Ensure GHCR container packages used by DOKS are publicly pullable.
#
# Root cause this guards: private packages + expired/revoked cluster ghcr-pull PAT
# → ImagePullBackOff with ghcr.io token 403/DENIED on staging/prod.
# Repo is public; packages may still be created private by default.
#
# Usage:
#   bash scripts/deploy/ghcr_ensure_public.sh
#   GHCR_OWNER=empiric2 GHCR_PACKAGE_PREFIX=tac-to-iwxxm bash scripts/deploy/ghcr_ensure_public.sh
#
# Env:
#   GH_TOKEN / GITHUB_TOKEN  required (packages:write)
#   GHCR_OWNER               default: empiric2 (org login, lowercase)
#   GHCR_PACKAGE_PREFIX      default: tac-to-iwxxm
#   GHCR_PACKAGES            default: backend frontend worker (space-separated suffixes)
#
# Traces: [Corpus: deploy] DOKS CD / GHCR → DOKS
set -euo pipefail

TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
if [[ -z "${TOKEN}" ]]; then
  echo "error: GH_TOKEN or GITHUB_TOKEN required" >&2
  exit 2
fi

OWNER="${GHCR_OWNER:-empiric2}"
PREFIX="${GHCR_PACKAGE_PREFIX:-tac-to-iwxxm}"
# shellcheck disable=SC2206
PACKAGES=(${GHCR_PACKAGES:-backend frontend worker})

api() {
  local method="$1" path="$2" data="${3:-}"
  if [[ -n "${data}" ]]; then
    curl -fsS -X "${method}" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -H "Content-Type: application/json" \
      --data "${data}" \
      "https://api.github.com${path}"
  else
    curl -fsS -X "${method}" \
      -H "Authorization: Bearer ${TOKEN}" \
      -H "Accept: application/vnd.github+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "https://api.github.com${path}"
  fi
}

encode() {
  # package names contain '/' — percent-encode for URL path
  python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}

for suffix in "${PACKAGES[@]}"; do
  name="${PREFIX}/${suffix}"
  enc="$(encode "${name}")"
  echo "Ensuring GHCR package public: ${OWNER}/${name}"

  # Prefer org API; fall back to user namespace if org package is missing.
  if ! vis="$(api GET "/orgs/${OWNER}/packages/container/${enc}" 2>/dev/null)"; then
    if ! vis="$(api GET "/user/packages/container/${enc}" 2>/dev/null)"; then
      echo "error: package not found via org or user API: ${name}" >&2
      exit 1
    fi
    scope="user"
  else
    scope="org"
  fi

  current="$(printf '%s' "${vis}" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("visibility","unknown"))')"
  echo "  current visibility=${current} (scope=${scope})"
  if [[ "${current}" == "public" ]]; then
    continue
  fi

  if [[ "${scope}" == "org" ]]; then
    api PUT "/orgs/${OWNER}/packages/container/${enc}/visibility" '{"visibility":"public"}' >/dev/null
  else
    api PUT "/user/packages/container/${enc}/visibility" '{"visibility":"public"}' >/dev/null
  fi
  echo "  updated visibility=public"
done

echo "GHCR packages are public for DOKS pull (anonymous or with pull secret)."
