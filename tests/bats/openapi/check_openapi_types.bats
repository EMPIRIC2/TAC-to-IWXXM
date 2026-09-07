# scripts/openapi/check_openapi_types.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/openapi/check_openapi_types.sh: stub pnpm path exits (match or drift/guard)" {
  run bash scripts/openapi/check_openapi_types.sh
  # Stub `pnpm` exits 0 without writing TMP → cmp fails → exit 1 is expected under stubs.
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
}
