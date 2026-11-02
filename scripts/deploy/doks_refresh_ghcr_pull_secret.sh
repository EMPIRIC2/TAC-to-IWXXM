#!/usr/bin/env bash
# Refresh the DOKS ghcr-pull dockerconfig secret with a live GHCR credential.
#
# Used by Deploy / ops so pods can pull private GHCR packages when the
# long-lived cluster PAT is revoked. Prefer GH_TOKEN/GITHUB_TOKEN from Actions
# (packages:read/write); each Deploy refreshes the secret before rollout.
#
# Usage:
#   DOKS_NAMESPACE=metar-iwxxm-staging bash scripts/deploy/doks_refresh_ghcr_pull_secret.sh
#
# Env:
#   DOKS_NAMESPACE     required (or default metar-iwxxm)
#   GH_TOKEN/GITHUB_TOKEN  required
#   GHCR_USERNAME      default: github.actor / x-access-token
#   GHCR_SERVER        default: ghcr.io
#   SECRET_NAME        default: ghcr-pull
set -euo pipefail

NS="${DOKS_NAMESPACE:-metar-iwxxm}"
TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
USER="${GHCR_USERNAME:-${GITHUB_ACTOR:-x-access-token}}"
SERVER="${GHCR_SERVER:-ghcr.io}"
SECRET_NAME="${SECRET_NAME:-ghcr-pull}"

if [[ -z "${TOKEN}" ]]; then
  echo "error: GH_TOKEN or GITHUB_TOKEN required" >&2
  exit 2
fi

echo "Refreshing ${SECRET_NAME} in ns=${NS} (user=${USER} server=${SERVER})"
kubectl -n "${NS}" create secret docker-registry "${SECRET_NAME}" \
  --docker-server="${SERVER}" \
  --docker-username="${USER}" \
  --docker-password="${TOKEN}" \
  --dry-run=client -o yaml \
  | kubectl -n "${NS}" apply -f -

echo "Secret ${SECRET_NAME} applied."
