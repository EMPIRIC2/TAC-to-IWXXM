#!/usr/bin/env bash
# Sync wmo-im iwxxm-* snapshots into vendor/schemas/ per vendor/manifest.json.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MANIFEST="${ROOT}/vendor/manifest.json"

if [[ "${1:-}" == "--from-manifest" ]]; then
  shift
  if [[ -n "${1:-}" ]]; then
    MANIFEST="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
  fi
fi

exec uv run python "${ROOT}/scripts/vendor/sync_iwxxm.py" --manifest "${MANIFEST}"
