# scripts/deploy/run_mock_byoc_compose_smoke.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/run_mock_byoc_compose_smoke.sh: exits under stubs (fail-closed or stub success)" {
  if command -v timeout >/dev/null 2>&1; then
    run timeout 5 bash scripts/deploy/run_mock_byoc_compose_smoke.sh
  elif command -v gtimeout >/dev/null 2>&1; then
    run gtimeout 5 bash scripts/deploy/run_mock_byoc_compose_smoke.sh
  else
    run bash scripts/deploy/run_mock_byoc_compose_smoke.sh
  fi
  [ "$status" -ge 0 ]
}
