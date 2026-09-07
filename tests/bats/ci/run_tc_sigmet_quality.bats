# scripts/ci/run_tc_sigmet_quality.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/run_tc_sigmet_quality.sh: main path with stubbed tooling" {
  run bash "scripts/ci/run_tc_sigmet_quality.sh"
  [ "$status" -eq 0 ]
}
