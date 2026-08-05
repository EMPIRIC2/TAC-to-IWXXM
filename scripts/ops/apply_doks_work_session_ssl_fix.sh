#!/usr/bin/env bash
# Apply T7.1 interim ConfigMap mount for work_session_service sslmode rewrite.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NS="${DOKS_NAMESPACE:-metar-iwxxm}"
SRC="$ROOT/apps/backend/src/services/work_session_service.py"

kubectl -n "$NS" create configmap work-session-ssl-fix \
  --from-file=work_session_service.py="$SRC" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Applied work-session-ssl-fix from $SRC"
echo "Ensure deploy/metar-api mounts this ConfigMap (see deployment-api.yaml)."
