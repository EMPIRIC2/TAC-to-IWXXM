# scripts/deploy/doks_host_header_smoke.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/doks_host_header_smoke.sh: stubbed host-header checks pass" {
  run bash scripts/deploy/doks_host_header_smoke.sh
  [ "$status" -eq 0 ]
}
