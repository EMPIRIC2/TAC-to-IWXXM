# scripts/ci/staging_gate.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/ci/staging_gate.sh: skip when event is not pull_request" {
  run env GITHUB_EVENT_NAME=push GITHUB_REPOSITORY=test/r GITHUB_SHA=abc123 GITHUB_BASE_REF=main \
    bash scripts/ci/staging_gate.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"skip"* ]]
}

@test "scripts/ci/staging_gate.sh: fail closed without required GitHub env" {
  # Actions always sets GITHUB_*; clear so ${VAR:?} fail-closed is measurable.
  run env -u GITHUB_REPOSITORY -u GITHUB_EVENT_NAME -u GITHUB_SHA \
    -u GITHUB_BASE_REF -u GITHUB_HEAD_REF -u GITHUB_EVENT_PATH -u GITHUB_TOKEN \
    bash scripts/ci/staging_gate.sh
  [ "$status" -ne 0 ]
}
