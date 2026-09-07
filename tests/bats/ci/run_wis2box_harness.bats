# scripts/ci/run_wis2box_harness.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/run_wis2box_harness.sh: fail closed when harness probe cannot connect" {
  if command -v timeout >/dev/null 2>&1; then
    run timeout 8 bash scripts/ci/run_wis2box_harness.sh
  elif command -v gtimeout >/dev/null 2>&1; then
    run gtimeout 8 bash scripts/ci/run_wis2box_harness.sh
  else
    run bash scripts/ci/run_wis2box_harness.sh
  fi
  [ "$status" -ne 0 ]
}
