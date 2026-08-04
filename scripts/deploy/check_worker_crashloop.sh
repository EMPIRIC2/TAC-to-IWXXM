#!/usr/bin/env bash
# EV-033 / F8 — alert-style check: fail if metar-worker is CrashLoopBackOff
# or has excessive restarts (use in smoke / cron / CI with cluster creds).
#
# Usage:
#   bash scripts/deploy/check_worker_crashloop.sh
#   MAX_RESTARTS=3 bash scripts/deploy/check_worker_crashloop.sh
set -euo pipefail

NS="${METAR_DOKS_NAMESPACE:-metar-iwxxm}"
SELECTOR="${METAR_WORKER_SELECTOR:-app.kubernetes.io/name=metar-worker}"
MAX_RESTARTS="${MAX_RESTARTS:-3}"

if ! command -v kubectl >/dev/null 2>&1; then
  echo "ERROR: kubectl required" >&2
  exit 2
fi

# Zero replicas is OK (intentional fail-closed) — not an alert.
REPLICAS="$(kubectl -n "${NS}" get deploy metar-worker -o jsonpath='{.spec.replicas}' 2>/dev/null || echo 0)"
if [[ "${REPLICAS}" == "0" || -z "${REPLICAS}" ]]; then
  echo "OK: metar-worker replicas=${REPLICAS:-missing} (fail-closed / not running)"
  exit 0
fi

POD_INFO="$(
  kubectl -n "${NS}" get pods -l "${SELECTOR}" \
    -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\t"}{.status.containerStatuses[0].state.waiting.reason}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}' \
    2>/dev/null || true
)"

if [[ -z "${POD_INFO}" ]]; then
  echo "ERROR: metar-worker replicas=${REPLICAS} but no pods found" >&2
  exit 1
fi

FAILED=0
while IFS=$'\t' read -r name phase waiting restarts; do
  [[ -z "${name}" ]] && continue
  restarts="${restarts:-0}"
  echo "pod=${name} phase=${phase} waiting=${waiting:-none} restarts=${restarts}"
  if [[ "${waiting}" == "CrashLoopBackOff" ]]; then
    echo "ALERT: ${name} is CrashLoopBackOff — check INGEST_POLLER_URL" >&2
    FAILED=1
  fi
  if [[ "${restarts}" =~ ^[0-9]+$ ]] && [[ "${restarts}" -gt "${MAX_RESTARTS}" ]]; then
    echo "ALERT: ${name} restartCount=${restarts} > ${MAX_RESTARTS}" >&2
    FAILED=1
  fi
done <<<"${POD_INFO}"

if [[ "${FAILED}" -eq 1 ]]; then
  exit 1
fi
echo "OK: metar-worker pods healthy (no CrashLoopBackOff; restarts ≤ ${MAX_RESTARTS})"
exit 0
