# scripts/frontend/audit-ci.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/frontend/audit-ci.sh: retired audit endpoint treated as skip" {
  run bash scripts/frontend/audit-ci.sh
  [ "$status" -eq 0 ]
}
