# scripts/ci/run_mutation_python.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/run_mutation_python.sh: usage when target missing" {
  run bash scripts/ci/run_mutation_python.sh
  [ "$status" -eq 2 ]
}

@test "scripts/ci/run_mutation_python.sh: stubbed backend mutation path" {
  run bash scripts/ci/run_mutation_python.sh backend
  [ "$status" -eq 0 ]
}
