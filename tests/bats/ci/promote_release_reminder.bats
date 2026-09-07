# scripts/ci/promote_release_reminder.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/promote_release_reminder.sh: skip outside stage→main PR context" {
  # Actions injects GITHUB_* on stage→main PRs; clear so the skip path is measurable
  # (otherwise stub git makes cd fail — BUG-2026-08-28).
  run env -u GITHUB_EVENT_NAME -u GITHUB_BASE_REF -u GITHUB_HEAD_REF \
    bash scripts/ci/promote_release_reminder.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"skip"* ]]
}
