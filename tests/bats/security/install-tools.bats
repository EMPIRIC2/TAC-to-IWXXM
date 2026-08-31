# scripts/security/install-tools.sh — bats coverage (EV-049)
load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/security/install-tools.sh: is executable and has shebang" {
  [ -x scripts/security/install-tools.sh ]
  run head -1 scripts/security/install-tools.sh
  [[ "$output" == *"bash"* ]]
}
