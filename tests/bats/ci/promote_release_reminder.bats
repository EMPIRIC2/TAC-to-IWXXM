# scripts/ci/promote_release_reminder.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/promote_release_reminder.sh: skip outside stage→main PR context" {
  run bash scripts/ci/promote_release_reminder.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"skip"* ]]
}
