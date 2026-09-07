# scripts/supabase/local-dev.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/supabase/local-dev.sh: invalid command exits non-zero" {
  run bash scripts/supabase/local-dev.sh invalid-cmd
  [ "$status" -eq 1 ]
}

@test "scripts/supabase/local-dev.sh: status with stub supabase" {
  run bash scripts/supabase/local-dev.sh status
  [ "$status" -eq 0 ]
}
