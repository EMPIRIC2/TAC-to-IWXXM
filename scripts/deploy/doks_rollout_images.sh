#!/usr/bin/env bash
# Pin DOKS Deployments to an immutable GHCR TIMESTAMP-SHA tag and wait for rollout.
#
# Usage:
#   bash scripts/deploy/doks_rollout_images.sh <image_tag>
#   IMAGE_TAG=20260805003332-5245f8d bash scripts/deploy/doks_rollout_images.sh
#
# Env:
#   DOKS_NAMESPACE   default: metar-iwxxm
#   GHCR_OWNER_REPO  default: empiric2/tac-to-iwxxm
#   ROLLOUT_TIMEOUT  default: 180s
#
# Traces: F30 AC7 / TC-F30-007 / S042 / EV-034 / E34-1..2
set -euo pipefail

TAG="${1:-${IMAGE_TAG:-}}"
if [[ -z "${TAG}" ]]; then
  echo "usage: $0 <image_tag>" >&2
  exit 2
fi

NS="${DOKS_NAMESPACE:-metar-iwxxm}"
OWNER="${GHCR_OWNER_REPO:-empiric2/tac-to-iwxxm}"
TIMEOUT="${ROLLOUT_TIMEOUT:-180s}"
REGISTRY="${GHCR_REGISTRY:-ghcr.io}"

API_IMG="${REGISTRY}/${OWNER}/backend:${TAG}"
FE_IMG="${REGISTRY}/${OWNER}/frontend:${TAG}"
WORKER_IMG="${REGISTRY}/${OWNER}/worker:${TAG}"

echo "DOKS rollout ns=${NS} tag=${TAG}"
echo "  metar-api      -> ${API_IMG}"
echo "  metar-frontend -> ${FE_IMG}"
echo "  metar-worker   -> ${WORKER_IMG}"

kubectl -n "${NS}" set image "deploy/metar-api" "api=${API_IMG}"
kubectl -n "${NS}" set image "deploy/metar-frontend" "frontend=${FE_IMG}"
kubectl -n "${NS}" set image "deploy/metar-worker" "worker=${WORKER_IMG}"

kubectl -n "${NS}" rollout status "deploy/metar-api" --timeout="${TIMEOUT}"
kubectl -n "${NS}" rollout status "deploy/metar-frontend" --timeout="${TIMEOUT}"
kubectl -n "${NS}" rollout status "deploy/metar-worker" --timeout="${TIMEOUT}"

echo "DOKS rollout complete:"
kubectl -n "${NS}" get deploy metar-api metar-frontend metar-worker \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.template.spec.containers[*]}{.name}={.image}{" "}{end}{"\n"}{end}'
