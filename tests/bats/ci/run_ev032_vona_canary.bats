# scripts/ci/run_ev032_vona_canary.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/run_ev032_vona_canary.sh: main path with stubbed tooling" {
  run bash "scripts/ci/run_ev032_vona_canary.sh"
  [ "$status" -eq 0 ]
}
