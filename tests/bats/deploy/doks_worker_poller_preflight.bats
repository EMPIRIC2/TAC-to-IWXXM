# scripts/deploy/doks_worker_poller_preflight.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/doks_worker_poller_preflight.sh: --help documents usage" {
  run bash scripts/deploy/doks_worker_poller_preflight.sh --help
  [ "$status" -eq 0 ]
}

@test "scripts/deploy/doks_worker_poller_preflight.sh: preflight OK with stub kubectl secret" {
  # Prefer bats kubectl stub even if the runner has a real kubectl earlier on PATH.
  helpers_bin="$(cd "${BATS_TEST_DIRNAME}/../helpers/bin" && pwd)"
  run env PATH="${helpers_bin}:${PATH}" bash scripts/deploy/doks_worker_poller_preflight.sh
  if [[ "$status" -ne 0 ]]; then
    echo "preflight status=${status} output=${output}" >&2
  fi
  [ "$status" -eq 0 ]
  [[ "$output" == *"Preflight OK"* ]]
}
