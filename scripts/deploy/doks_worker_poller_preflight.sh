#!/usr/bin/env bash
# EV-033 / F8 — fail-closed DOKS worker scale around INGEST_POLLER_URL.
# Rejects REPLACE_ME_* / non-https; scales to 0 when --fail-closed or bad --scale-up.
#
# Reads metar-worker-secrets, validates the URL, optionally probes HTTPS,
# scales to 0 when invalid, and only scales to 1 when --scale-up and valid.
#
# Usage:
#   bash scripts/deploy/doks_worker_poller_preflight.sh
#   bash scripts/deploy/doks_worker_poller_preflight.sh --probe
#   bash scripts/deploy/doks_worker_poller_preflight.sh --probe --scale-up
#   bash scripts/deploy/doks_worker_poller_preflight.sh --fail-closed   # scale 0 if bad
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NS="${METAR_DOKS_NAMESPACE:-metar-iwxxm}"
SECRET="${METAR_WORKER_SECRET:-metar-worker-secrets}"
DEPLOY="${METAR_WORKER_DEPLOY:-metar-worker}"
PROBE=0
SCALE_UP=0
FAIL_CLOSED=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --probe) PROBE=1; shift ;;
    --scale-up) SCALE_UP=1; shift ;;
    --fail-closed) FAIL_CLOSED=1; shift ;;
    -h|--help)
      sed -n '2,12p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if ! command -v kubectl >/dev/null 2>&1; then
  echo "ERROR: kubectl required" >&2
  exit 2
fi

URL="$(
  kubectl -n "${NS}" get secret "${SECRET}" -o jsonpath='{.data.INGEST_POLLER_URL}' \
    | python3 -c 'import sys,base64; print(base64.b64decode(sys.stdin.read()).decode())'
)"

ARGS=("${URL}")
if [[ "${PROBE}" -eq 1 ]]; then
  ARGS+=(--probe)
fi

set +e
python3 "${ROOT}/scripts/deploy/validate_ingest_poller_url.py" "${ARGS[@]}"
RC=$?
set -e

if [[ "${RC}" -ne 0 ]]; then
  echo "Preflight FAILED for ${NS}/${SECRET} INGEST_POLLER_URL" >&2
  if [[ "${FAIL_CLOSED}" -eq 1 || "${SCALE_UP}" -eq 1 ]]; then
    echo "Scaling ${DEPLOY} → 0 (fail-closed)" >&2
    kubectl -n "${NS}" scale "deploy/${DEPLOY}" --replicas=0
  fi
  exit "${RC}"
fi

echo "Preflight OK for ${DEPLOY}"
if [[ "${SCALE_UP}" -eq 1 ]]; then
  kubectl -n "${NS}" scale "deploy/${DEPLOY}" --replicas=1
  kubectl -n "${NS}" rollout status "deploy/${DEPLOY}" --timeout=120s
fi
exit 0
