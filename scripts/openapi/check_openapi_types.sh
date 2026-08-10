#!/usr/bin/env bash
# Fail if apps/frontend/src/generated/openapi.d.ts drifts from openapi/openapi.json.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
FE="$ROOT/apps/frontend"
TMP="$(mktemp -t openapi-types.XXXXXX.d.ts)"
cleanup() { rm -f "$TMP"; }
trap cleanup EXIT

cd "$FE"
pnpm exec openapi-typescript openapi/openapi.json -o "$TMP"
if ! cmp -s "$TMP" src/generated/openapi.d.ts; then
  echo "error: openapi.d.ts drift — run: pnpm --filter @metar/frontend openapi:generate" >&2
  echo "       (after make openapi-refresh if the FastAPI schema changed)" >&2
  diff -u src/generated/openapi.d.ts "$TMP" | head -n 80 || true
  exit 1
fi
echo "openapi.d.ts matches openapi/openapi.json"
