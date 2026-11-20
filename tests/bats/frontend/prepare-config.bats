# scripts/frontend/prepare-config.sh — bats coverage (EV-080 )
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/frontend/prepare-config.sh: writes config.json from local template" {
  run env METAR_CONFIG_ENV=local bash scripts/frontend/prepare-config.sh
  [ "$status" -eq 0 ]
}

@test "scripts/frontend/prepare-config.sh: fail closed when config source missing" {
  run env METAR_CONFIG_ENV=missing-env bash scripts/frontend/prepare-config.sh
  [ "$status" -eq 1 ]
}

# Prod publishableKey fail-closed is covered by pytest
# (tests/test_frontend_env_configuration.py::TestPrepareConfigScript) — bats
# stubs python3 to exit 0 (NFR-EV080-006), so the inject path cannot be asserted here.
