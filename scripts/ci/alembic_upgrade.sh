#!/usr/bin/env bash
# Idempotent Alembic upgrade against DATABASE_URL / ALEMBIC_DATABASE_URL (F30 / ADR-033).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT/apps/backend"

if [[ -z "${DATABASE_URL:-}" && -z "${ALEMBIC_DATABASE_URL:-}" ]]; then
  echo "error: set DATABASE_URL or ALEMBIC_DATABASE_URL" >&2
  exit 1
fi

# Prefer ALEMBIC_DATABASE_URL when both set (env.py reads it first).
export DATABASE_URL="${ALEMBIC_DATABASE_URL:-$DATABASE_URL}"

uv run alembic -c alembic.ini upgrade head
