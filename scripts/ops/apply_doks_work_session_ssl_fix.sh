#!/usr/bin/env bash
# DEPRECATED (BUG-2026-08-10): sslmode rewrite is in-image via _sync_database_url.
# Do not remount work_session_service.py — stale ConfigMaps caused staging
# NameError: UUID. Kept only to delete leftover ConfigMaps if needed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
NS="${DOKS_NAMESPACE:-metar-iwxxm}"

echo "DEPRECATED: refusing to create work-session-ssl-fix."
echo "Remove any leftover mount from deploy/doks/base/deployment-api.yaml (already done)."
echo "Optional cleanup: kubectl -n $NS delete configmap work-session-ssl-fix --ignore-not-found"
echo "Source of truth: $ROOT/apps/backend/src/services/work_session_service.py (in image)."
exit 1
