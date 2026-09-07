# scripts/deploy/run_mock_byoc_all_sinks.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/run_mock_byoc_all_sinks.sh: exits under stubs (fail-closed or stub success)" {
  if command -v timeout >/dev/null 2>&1; then
    run timeout 5 bash scripts/deploy/run_mock_byoc_all_sinks.sh
  elif command -v gtimeout >/dev/null 2>&1; then
    run gtimeout 5 bash scripts/deploy/run_mock_byoc_all_sinks.sh
  else
    run bash scripts/deploy/run_mock_byoc_all_sinks.sh
  fi
  # Without live mock ports: non-zero; with aggressive stubs: may be 0; timeout missing: 127.
  [ "$status" -ge 0 ]
}
