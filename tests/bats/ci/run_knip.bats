# scripts/ci/run_knip.sh — bats coverage (EV-quality-tooling-suite)
# [Corpus: tests]

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/run_knip.sh: knip exits 0 with configured allowlists" {
  run bash scripts/ci/run_knip.sh
  [ "$status" -eq 0 ]
  [ -f .quality-reports/knip.txt ]
}
