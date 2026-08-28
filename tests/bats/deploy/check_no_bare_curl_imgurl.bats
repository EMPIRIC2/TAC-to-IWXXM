# scripts/deploy/check_no_bare_curl_imgurl.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/check_no_bare_curl_imgurl.sh: ci-cd workflow uses resilient deploy trigger" {
  run bash scripts/deploy/check_no_bare_curl_imgurl.sh
  [ "$status" -eq 0 ]
}
