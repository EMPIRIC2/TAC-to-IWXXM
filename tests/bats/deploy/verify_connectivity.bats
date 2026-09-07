# scripts/deploy/verify_connectivity.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/verify_connectivity.sh: offline H0c path with stub uv" {
  run bash scripts/deploy/verify_connectivity.sh
  [ "$status" -eq 0 ]
}
