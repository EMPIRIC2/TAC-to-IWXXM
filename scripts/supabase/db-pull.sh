#!/usr/bin/env bash
# Pull the linked remote schema into a new supabase/migrations file.
#
# Preflights migration list so pg-delta SSL material exists under
# supabase/.temp/pgdelta/ before db pull caches the migrations catalog.
# Without this, CLI 2.107 can warn:
#   failed to cache migrations catalog ... pgdelta-target-ca.crt ENOENT
#
# Prerequisites:
#   supabase login           (or export SUPABASE_ACCESS_TOKEN='sbp_...')
#   supabase link --project-ref ktvxijislbtgqapllmuk
#
# Usage:
#   bash scripts/supabase/db-pull.sh                 # pull public schema
#   bash scripts/supabase/db-pull.sh my_migration    # name the migration file
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_REF="${SUPABASE_PROJECT_REF:-ktvxijislbtgqapllmuk}"
PGDELTA_DIR="$ROOT/supabase/.temp/pgdelta"
PGDELTA_CA="$PGDELTA_DIR/pgdelta-target-ca.crt"
MIGRATION_NAME="${1:-}"

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
  echo "      db pull may still succeed; catalog cache warning is possible." >&2
  echo "      Retry after: supabase link --project-ref ${PROJECT_REF}" >&2
fi

echo "Running supabase db pull --linked..."
supabase db pull --linked $MIGRATION_NAME

echo "Done. Review the new file under supabase/migrations/ before committing."
