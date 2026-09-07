# scripts/deploy/check_worker_crashloop.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/check_worker_crashloop.sh: OK when worker replicas are zero" {
  run bash scripts/deploy/check_worker_crashloop.sh
  [ "$status" -eq 0 ]
}
