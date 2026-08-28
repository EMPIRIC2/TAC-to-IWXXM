# scripts/deploy/doks_rollout_images.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/doks_rollout_images.sh: usage when image tag missing" {
  run bash scripts/deploy/doks_rollout_images.sh
  [ "$status" -eq 2 ]
}

@test "scripts/deploy/doks_rollout_images.sh: stubbed rollout with tag" {
  run bash scripts/deploy/doks_rollout_images.sh 20260805003332-deadbeef
  [ "$status" -eq 0 ]
}
