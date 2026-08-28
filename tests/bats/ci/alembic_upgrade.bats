# scripts/ci/alembic_upgrade.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/alembic_upgrade.sh: fail closed without DATABASE_URL" {
  # CI often exports DATABASE_URL; clear both names so fail-closed is measurable.
  run env -u DATABASE_URL -u ALEMBIC_DATABASE_URL bash scripts/ci/alembic_upgrade.sh
  [ "$status" -eq 1 ]
}

@test "scripts/ci/alembic_upgrade.sh: stubbed upgrade with DATABASE_URL" {
  run env DATABASE_URL=postgresql://stub/stub bash scripts/ci/alembic_upgrade.sh
  [ "$status" -eq 0 ]
}
