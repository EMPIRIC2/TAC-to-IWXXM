# scripts/ci/run_deptry_all.sh — bats coverage (EV-quality-tooling-suite)
# [Corpus: tests]

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/run_deptry_all.sh: all members pass (or tool installs via uv)" {
  run bash scripts/ci/run_deptry_all.sh
  [ "$status" -eq 0 ]
  [ -f .quality-reports/deptry/summary.txt ]
}
