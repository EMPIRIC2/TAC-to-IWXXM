# scripts/ci/run_quality_matrices_smoke.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/run_quality_matrices_smoke.sh: main path with stubbed tooling" {
  run bash "scripts/ci/run_quality_matrices_smoke.sh"
  [ "$status" -eq 0 ]
}
