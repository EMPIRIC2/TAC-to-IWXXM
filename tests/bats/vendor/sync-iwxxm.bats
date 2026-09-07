# scripts/vendor/sync-iwxxm.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/vendor/sync-iwxxm.sh: main path with stubbed tooling" {
  run bash "scripts/vendor/sync-iwxxm.sh"
  [ "$status" -eq 0 ]
}
