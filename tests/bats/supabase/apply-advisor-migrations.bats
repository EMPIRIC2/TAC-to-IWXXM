# scripts/supabase/apply-advisor-migrations.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/supabase/apply-advisor-migrations.sh: dry-run lists migrations" {
  run bash scripts/supabase/apply-advisor-migrations.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"Dry run"* ]]
}
