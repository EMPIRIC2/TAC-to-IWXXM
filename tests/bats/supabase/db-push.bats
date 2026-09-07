# scripts/supabase/db-push.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/supabase/db-push.sh: fail closed without linked project" {
  ref="${REPO_ROOT}/supabase/.temp/project-ref"
  backup=""
  if [[ -f "$ref" ]]; then
    backup="$(mktemp)"
    mv "$ref" "$backup"
  fi
  run bash scripts/supabase/db-push.sh
  rc=$status
  if [[ -n "$backup" ]]; then
    mv "$backup" "$ref"
  fi
  [ "$rc" -eq 1 ]
}
