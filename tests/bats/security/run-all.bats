# scripts/security/run-all.sh — bats coverage (EV-049)
load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/security/run-all.sh: is executable and has shebang" {
  [ -x scripts/security/run-all.sh ]
  run head -1 scripts/security/run-all.sh
  [[ "$output" == *"bash"* ]]
}
