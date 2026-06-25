#!/usr/bin/env bash
# Push pending supabase/migrations to the linked remote project.
#
# Preflights migration list so pg-delta SSL material exists under
# supabase/.temp/pgdelta/ before db push caches the migrations catalog.
# Without this, CLI 2.107 can warn:
#   failed to cache migrations catalog ... pgdelta-target-ca.crt ENOENT
# even when migrations apply successfully.
#
# Prerequisites:
#   export SUPABASE_ACCESS_TOKEN='sbp_...'
#   supabase link --project-ref ktvxijislbtgqapllmuk
#
# Usage:
#   bash scripts/supabase/db-push.sh
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_REF="${SUPABASE_PROJECT_REF:-ktvxijislbtgqapllmuk}"
PGDELTA_DIR="$ROOT/supabase/.temp/pgdelta"
PGDELTA_CA="$PGDELTA_DIR/pgdelta-target-ca.crt"

if ! command -v supabase >/dev/null 2>&1; then
  echo "ERROR: supabase CLI not found. Install: https://supabase.com/docs/guides/cli" >&2
  exit 1
fi

if [[ -z "${SUPABASE_ACCESS_TOKEN:-}" ]]; then
  echo "NOTE: SUPABASE_ACCESS_TOKEN not set; relying on 'supabase login' credentials." >&2
  echo "      If auth fails, run: export SUPABASE_ACCESS_TOKEN='sbp_...'  or  supabase login" >&2
elif [[ "${SUPABASE_ACCESS_TOKEN}" != sbp_* ]]; then
  echo "NOTE: Ignoring SUPABASE_ACCESS_TOKEN (not sbp_...); using 'supabase login' credentials." >&2
  unset SUPABASE_ACCESS_TOKEN
fi

cd "$ROOT"

LINKED_REF=""
if [[ -f supabase/.temp/project-ref ]]; then
  LINKED_REF="$(tr -d '[:space:]' < supabase/.temp/project-ref)"
fi

if [[ -z "$LINKED_REF" ]]; then
  echo "ERROR: No linked Supabase project. Run from repo root:" >&2
  echo "  supabase link --project-ref ${PROJECT_REF}" >&2
  exit 1
fi

if [[ "$LINKED_REF" != "$PROJECT_REF" ]]; then
  echo "WARN: linked project is ${LINKED_REF}, expected ${PROJECT_REF}." >&2
fi

echo "Preflight: migration list --linked (warms pg-delta SSL certs for ${LINKED_REF})..."
supabase migration list --linked

if [[ ! -f "$PGDELTA_CA" ]]; then
  echo "WARN: ${PGDELTA_CA} missing after migration list." >&2
  echo "      db push may still apply migrations; catalog cache warning is possible." >&2
  echo "      Retry after: supabase link --project-ref ${PROJECT_REF}" >&2
fi

echo "Running supabase db push --linked..."
supabase db push --linked

echo "Done."
