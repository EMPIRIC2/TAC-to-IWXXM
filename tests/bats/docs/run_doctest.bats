# scripts/docs/run_doctest.sh — bats coverage

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/docs/run_doctest.sh: exists and is executable" {
  [ -f "scripts/docs/run_doctest.sh" ]
  [ -x "scripts/docs/run_doctest.sh" ]
}
