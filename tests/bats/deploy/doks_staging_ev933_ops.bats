# scripts/deploy/doks_staging_ev933_ops.sh — bats coverage (EV-933 / EV-080)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/doks_staging_ev933_ops.sh: stubbed staging Alembic + HMAC ops" {
  rm -f "${BATS_TMPDIR}/kubectl-ev933-hmac-state"
  run bash scripts/deploy/doks_staging_ev933_ops.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"EV-933 staging ops complete"* ]]
  [[ "$output" == *"PROFILE_OVERLAY_HMAC_SECRET: added"* ]]
}
