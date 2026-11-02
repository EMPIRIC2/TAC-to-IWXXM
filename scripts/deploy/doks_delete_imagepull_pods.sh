#!/usr/bin/env bash
# Best-effort delete of pods stuck in ImagePullBackOff / ErrImagePull.
# Usage: DOKS_NAMESPACE=metar-iwxxm-staging bash scripts/deploy/doks_delete_imagepull_pods.sh
set -euo pipefail

NS="${DOKS_NAMESPACE:-metar-iwxxm}"

kubectl -n "${NS}" get pods -o json | python3 -c '
import json, sys
data = json.load(sys.stdin)
for pod in data.get("items", []):
    name = pod["metadata"]["name"]
    statuses = (pod.get("status", {}).get("containerStatuses") or []) + (
        pod.get("status", {}).get("initContainerStatuses") or []
    )
    for cs in statuses:
        waiting = (cs.get("state") or {}).get("waiting") or {}
        if waiting.get("reason") in ("ImagePullBackOff", "ErrImagePull"):
            print(name)
            break
' | while read -r pod; do
  echo "Deleting stuck pod ${pod}"
  kubectl -n "${NS}" delete pod "${pod}" --wait=false || true
done
