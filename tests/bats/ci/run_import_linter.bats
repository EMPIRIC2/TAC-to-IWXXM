# scripts/ci/run_import_linter.sh — bats coverage (EV-quality-tooling-suite)
# [Corpus: tests]

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/run_import_linter.sh: contracts keep (or tool installs via uv)" {
  run bash scripts/ci/run_import_linter.sh
  [ "$status" -eq 0 ]
  [ -f .quality-reports/import-linter.txt ]
}
