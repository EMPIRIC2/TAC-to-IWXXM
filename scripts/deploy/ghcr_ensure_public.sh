#!/usr/bin/env bash
# Best-effort: mark GHCR container packages public for anonymous DOKS pulls.
#
# GITHUB_TOKEN often lacks permission to change org package visibility (API
# returns 404). Prefer scripts/deploy/doks_refresh_ghcr_pull_secret.sh for
# reliable pulls; this script is advisory and does not fail the job on PUT 404.
#
# Usage:
#   bash scripts/deploy/ghcr_ensure_public.sh
#
# Env:
#   GH_TOKEN / GITHUB_TOKEN  required
#   GHCR_OWNER               default: empiric2
#   GHCR_PACKAGE_PREFIX      default: tac-to-iwxxm
#   GHCR_PACKAGES            default: backend frontend worker
#   GHCR_ENSURE_PUBLIC_STRICT  if 1, exit non-zero on visibility update failure
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
STRICT="${GHCR_ENSURE_PUBLIC_STRICT:-0}"
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
  python3 -c 'import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}

failed=0
for suffix in "${PACKAGES[@]}"; do
  name="${PREFIX}/${suffix}"
  enc="$(encode "${name}")"
  echo "Ensuring GHCR package public: ${OWNER}/${name}"

  if ! vis="$(api GET "/orgs/${OWNER}/packages/container/${enc}" 2>/dev/null)"; then
    if ! vis="$(api GET "/user/packages/container/${enc}" 2>/dev/null)"; then
      echo "warning: package not found via org or user API: ${name}" >&2
      failed=1
      continue
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
    path="/orgs/${OWNER}/packages/container/${enc}/visibility"
  else
    path="/user/packages/container/${enc}/visibility"
  fi

  if api PUT "${path}" '{"visibility":"public"}' >/dev/null 2>&1; then
    echo "  updated visibility=public"
  else
    echo "warning: could not set visibility=public for ${name} (GITHUB_TOKEN may lack package admin)." >&2
    echo "  Use doks_refresh_ghcr_pull_secret.sh so DOKS can pull with a live token." >&2
    failed=1
  fi
done

if [[ "${failed}" -ne 0 ]]; then
  if [[ "${STRICT}" == "1" ]]; then
    echo "error: one or more packages remain non-public (strict mode)" >&2
    exit 1
  fi
  echo "GHCR ensure-public finished with warnings (non-fatal)."
  exit 0
fi

echo "GHCR packages are public for DOKS pull (anonymous or with pull secret)."
