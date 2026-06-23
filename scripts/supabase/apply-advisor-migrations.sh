#!/usr/bin/env bash
# Apply METAR Supabase advisor remediation migrations (003–005) to the linked project.
#
# Prerequisites:
#   - Supabase CLI installed and logged in (`supabase login`)
#   - Project linked: `supabase link --project-ref ktvxijislbtgqapllmuk`
#
# Usage:
#   bash scripts/supabase/apply-advisor-migrations.sh          # dry-run list
#   bash scripts/supabase/apply-advisor-migrations.sh --apply  # push via CLI
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MIGRATIONS_DIR="$ROOT/apps/frontend/supabase/migrations"
PROJECT_REF="${SUPABASE_PROJECT_REF:-ktvxijislbtgqapllmuk}"

APPLY=0
if [[ "${1:-}" == "--apply" ]]; then
  APPLY=1
fi

echo "METAR Supabase advisor migrations (project: ${PROJECT_REF})"
echo

for file in \
  "$MIGRATIONS_DIR/003_supabase_advisor_remediation.sql" \
  "$MIGRATIONS_DIR/004_supabase_advisor_policy_cleanup.sql" \
  "$MIGRATIONS_DIR/005_supabase_advisor_remediation.sql"
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
  echo "Dry run only. Re-run with --apply to execute: supabase db push"
  echo "Or paste each migration into Supabase Dashboard → SQL Editor."
  exit 0
fi

if ! command -v supabase >/dev/null 2>&1; then
  echo "ERROR: supabase CLI not found. Install: https://supabase.com/docs/guides/cli" >&2
  exit 1
fi

cd "$ROOT/apps/frontend"
echo "Running supabase db push..."
supabase db push --project-ref "$PROJECT_REF"

echo
echo "Post-apply: open Supabase Dashboard → Database → Advisors (security + performance)."
echo "Target: zero ERROR/WARN on user_profiles and METAR evaluation tables."
