# scripts/deploy/doks_provisional_live_env.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/doks_provisional_live_env.sh: exports provisional DOKS env vars" {
  run bash scripts/deploy/doks_provisional_live_env.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"PLAYWRIGHT_DOKS_PROVISIONAL=1"* ]]
}
