# scripts/deploy/apply_gh_branch_rulesets.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/apply_gh_branch_rulesets.sh: stubbed gh ruleset apply" {
  run bash scripts/deploy/apply_gh_branch_rulesets.sh
  [ "$status" -eq 0 ]
}
