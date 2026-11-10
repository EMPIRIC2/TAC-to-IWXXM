# scripts/ci/generate_sbom.sh — bats coverage (EV-080 / ADR-007)
# Stub: assert the script exists and is executable; do not hit the network.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/generate_sbom.sh: is present and executable" {
  [ -x scripts/ci/generate_sbom.sh ]
  run head -n 1 scripts/ci/generate_sbom.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"bash"* ]] || [[ "$output" == *"#!"* ]]
}
