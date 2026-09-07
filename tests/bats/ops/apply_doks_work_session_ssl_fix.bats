# scripts/ops/apply_doks_work_session_ssl_fix.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ops/apply_doks_work_session_ssl_fix.sh: deprecated script exits non-zero" {
  run bash scripts/ops/apply_doks_work_session_ssl_fix.sh
  [ "$status" -eq 1 ]
  [[ "$output" == *"DEPRECATED"* ]]
}
