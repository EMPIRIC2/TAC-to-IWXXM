#!/usr/bin/env bash
# Local Supabase stack helpers (repo root supabase/ per Supabase CLI best practices).
#
# Prerequisites: Docker, Supabase CLI (`npm install -g supabase` or https://supabase.com/docs/guides/cli)
#
# Usage:
#   bash scripts/supabase/local-dev.sh status
#   bash scripts/supabase/local-dev.sh start
#   bash scripts/supabase/local-dev.sh reset
#   bash scripts/supabase/local-dev.sh stop
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if ! command -v supabase >/dev/null 2>&1; then
  echo "ERROR: supabase CLI not found. Install: npm install -g supabase" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker not found. Local Supabase requires Docker." >&2
  exit 1
fi

ensure_running() {
  if supabase status >/dev/null 2>&1; then
    return 0
  fi
  echo "Local Supabase stack is not running — starting (first run may take several minutes)..."
  supabase start
}

cmd="${1:-status}"

case "$cmd" in
  status)
    supabase status
    ;;
  start)
    ensure_running
    echo
    echo "Local stack ready. Point config/local.json supabase.url to http://127.0.0.1:54321"
    echo "Run 'supabase status' for publishable and secret keys for .env"
    ;;
  reset)
    ensure_running
    supabase db reset
    echo
    echo "Database reset complete (migrations + supabase/seed.sql)."
    ;;
  stop)
    supabase stop
    ;;
  *)
    echo "Usage: $0 {status|start|reset|stop}" >&2
    exit 1
    ;;
esac
