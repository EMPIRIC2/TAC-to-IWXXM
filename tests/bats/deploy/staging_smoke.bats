# scripts/deploy/staging_smoke.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/staging_smoke.sh: stubbed curl health probes pass" {
  run bash scripts/deploy/staging_smoke.sh
  [ "$status" -eq 0 ]
}
