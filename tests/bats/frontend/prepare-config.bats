# scripts/frontend/prepare-config.sh — bats coverage (EV-080 / ADR-007)
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
