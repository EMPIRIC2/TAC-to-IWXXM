# scripts/env/verify-sync.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/env/verify-sync.sh: config validation passes offline" {
  run bash scripts/env/verify-sync.sh
  [ "$status" -eq 0 ]
}
