# scripts/docs/run_doctest.sh — bats coverage

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/docs/run_doctest.sh: exists and is executable" {
  [ -f "scripts/docs/run_doctest.sh" ]
  [ -x "scripts/docs/run_doctest.sh" ]
}

@test "scripts/docs/run_doctest.sh: treats pytest exit 5 as success" {
  # TC-EVDOC-002/004 — Examples optional; empty doctest trees must not fail the gate.
  run grep -E 'ec.*-eq 5|pytest exit 5' scripts/docs/run_doctest.sh
  [ "$status" -eq 0 ]
}
