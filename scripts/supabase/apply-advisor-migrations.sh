#!/usr/bin/env bash
# Apply METAR Supabase advisor remediation migrations to the linked remote project.
#
# Canonical migrations live in supabase/migrations/ (timestamp-ordered).
# Local development: use `bash scripts/supabase/local-dev.sh reset` instead.
#
# Prerequisites:
#   - Supabase CLI installed and logged in (`supabase login`)
#   - Project linked from repo root: `supabase link --project-ref ktvxijislbtgqapllmuk`
#
# Usage:
#   bash scripts/supabase/apply-advisor-migrations.sh          # dry-run list
#   bash scripts/supabase/apply-advisor-migrations.sh --apply  # push via CLI
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MIGRATIONS_DIR="$ROOT/supabase/migrations"
PROJECT_REF="${SUPABASE_PROJECT_REF:-ktvxijislbtgqapllmuk}"

APPLY=0
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=1
fi

echo "METAR Supabase migrations (project: ${PROJECT_REF})"
echo "Directory: ${MIGRATIONS_DIR}"
echo

for file in \
  "$MIGRATIONS_DIR"/20250614000004_supabase_advisor_remediation.sql \
  "$MIGRATIONS_DIR"/20250614000005_supabase_advisor_policy_cleanup.sql \
  "$MIGRATIONS_DIR"/20250614000006_supabase_advisor_remediation.sql \
  "$MIGRATIONS_DIR"/20250623000007_metar_work_sessions.sql
do
  [[ -f "$file" ]] || { echo "Missing: $file" >&2; exit 1; }
  echo "  - $(basename "$file")"
done

echo
echo "Auth dashboard (manual — cannot be applied via SQL):"
echo "  1. Authentication → URL configuration → add prod + local redirect URLs"
echo "  2. Authentication → Password Security → enable Leaked password protection"
echo "  3. API Keys → create Publishable + Secret; disable legacy JWT keys after deploy"
echo

if [[ "$APPLY" -eq 0 ]]; then
  echo "Dry run only. Re-run with --apply to execute: bash scripts/supabase/db-push.sh"
  echo "Or paste each migration into Supabase Dashboard → SQL Editor."
  exit 0
fi

bash "$(dirname "${BASH_SOURCE[0]}")/db-push.sh"

echo
echo "Post-apply: open Supabase Dashboard → Database → Advisors (security + performance)."
echo "Target: zero ERROR/WARN on user_profiles and METAR evaluation tables."
