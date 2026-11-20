# scripts/ci/check_sbom_drift.sh — bats coverage (EV-080 )
# Stub: assert the script exists and is executable; do not regenerate SBOM here.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/check_sbom_drift.sh: is present and executable" {
  [ -x scripts/ci/check_sbom_drift.sh ]
  run head -n 1 scripts/ci/check_sbom_drift.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"bash"* ]] || [[ "$output" == *"#!"* ]]
}
