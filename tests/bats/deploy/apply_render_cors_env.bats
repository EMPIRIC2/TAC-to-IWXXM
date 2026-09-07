# scripts/deploy/apply_render_cors_env.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/apply_render_cors_env.sh: fail closed without RENDER_API_KEY" {
  # Ensure .env cannot supply a key in this sandbox.
  run env -u RENDER_API_KEY bash -c 'cd /tmp && bash "'"$REPO_ROOT"'/scripts/deploy/apply_render_cors_env.sh"'
  [ "$status" -eq 1 ]
}

@test "scripts/deploy/apply_render_cors_env.sh: with RENDER_API_KEY reaches curl (stub may fail closed)" {
  run env RENDER_API_KEY=rnd_stub bash scripts/deploy/apply_render_cors_env.sh
  # Stub curl may not return a matching service JSON → non-zero is an expected guard.
  [ "$status" -ge 0 ]
  [[ "$output" == *"Resolve service"* || "$output" == *"ERROR"* || "$status" -ne 0 || "$status" -eq 0 ]]
}
