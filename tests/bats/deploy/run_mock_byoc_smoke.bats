# scripts/deploy/run_mock_byoc_smoke.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/run_mock_byoc_smoke.sh: main path with stubbed tooling" {
  run bash "scripts/deploy/run_mock_byoc_smoke.sh"
  [ "$status" -eq 0 ]
}
