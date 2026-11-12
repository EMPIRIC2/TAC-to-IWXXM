# scripts/ci/run_depcruise.sh — bats coverage (EV-quality-tooling-suite)
# [Corpus: tests]

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/run_depcruise.sh: no dependency violations" {
  run bash scripts/ci/run_depcruise.sh
  [ "$status" -eq 0 ]
  [ -f .quality-reports/depcruise.txt ]
}
