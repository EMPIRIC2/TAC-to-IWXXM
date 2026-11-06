#!/usr/bin/env bash
# Run all available Supabase advisors via Management API and fail on ERROR.
#
# Used by:
#   - .github/workflows/supabase-sync.yml (advisors job)
#   - scripts/security/run-all.sh when SEC_SKIP_SUPABASE_ADVISORS!=1
#
# Env:
#   SUPABASE_ACCESS_TOKEN   required (sbp_… Dashboard → Account → Access Tokens)
#   SUPABASE_PROJECT_REF    optional (default ktvxijislbtgqapllmuk)
#   SEC_SUPABASE_ADVISORS_FAIL_ON  optional: none|info|warn|error (default error)
#
# Types fetched: security, performance, and health when the API exposes it.
# [Corpus: tech-spec] [Corpus: deploy] — docs/deploy.md §Supabase CI sync
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="${ROOT}/scripts/security/supabase_advisors.py"

if [[ ! -f "${SCRIPT}" ]]; then
  echo "[supabase-advisors] ERROR: missing ${SCRIPT}" >&2
  exit 1
fi

if [[ -z "${SUPABASE_ACCESS_TOKEN:-}" ]]; then
  echo "[supabase-advisors] ERROR: SUPABASE_ACCESS_TOKEN is required" >&2
  echo "Create at Supabase Dashboard → Account → Access Tokens; set GitHub Actions secret." >&2
  exit 1
fi

exec python3 "${SCRIPT}" --type all "$@"
