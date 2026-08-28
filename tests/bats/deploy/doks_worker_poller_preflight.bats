# scripts/deploy/doks_worker_poller_preflight.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/doks_worker_poller_preflight.sh: --help documents usage" {
  run bash scripts/deploy/doks_worker_poller_preflight.sh --help
  [ "$status" -eq 0 ]
}

@test "scripts/deploy/doks_worker_poller_preflight.sh: preflight OK with stub kubectl secret" {
  run bash scripts/deploy/doks_worker_poller_preflight.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"Preflight OK"* ]]
}
