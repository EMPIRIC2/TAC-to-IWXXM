# scripts/launchers/launch_api.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/launchers/launch_api.sh: --help exits zero" {
  run bash scripts/launchers/launch_api.sh --help
  [ "$status" -eq 0 ]
}
