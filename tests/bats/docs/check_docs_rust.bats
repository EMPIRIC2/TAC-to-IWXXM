# scripts/docs/check_docs_rust.sh — bats coverage (ADR-048)
# Map path: tests/bats/docs/check_docs_rust.bats per EV-080 (rel without .sh)

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/docs/check_docs_rust.sh: exists and is executable" {
  [ -f "scripts/docs/check_docs_rust.sh" ]
  [ -x "scripts/docs/check_docs_rust.sh" ]
}
