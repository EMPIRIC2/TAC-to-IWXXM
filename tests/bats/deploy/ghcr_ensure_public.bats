# scripts/deploy/ghcr_ensure_public.sh — bats coverage
# NFR: stub curl/python; no live GitHub calls.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/ghcr_ensure_public.sh: requires token" {
  unset GH_TOKEN GITHUB_TOKEN || true
  run bash scripts/deploy/ghcr_ensure_public.sh
  [ "$status" -eq 2 ]
}

@test "scripts/deploy/ghcr_ensure_public.sh: already-public packages succeed" {
  export GITHUB_TOKEN=test-token
  # Stub curl: GET returns public visibility JSON; PUT should not be needed.
  tmp="$(mktemp -d)"
  cat >"${tmp}/curl" <<'EOF'
#!/usr/bin/env bash
# Echo public package JSON for GET; accept PUT.
if [[ "$*" == *"/visibility"* ]]; then
  exit 0
fi
echo '{"visibility":"public","name":"tac-to-iwxxm/backend"}'
EOF
  chmod +x "${tmp}/curl"
  PATH="${tmp}:$PATH" run bash scripts/deploy/ghcr_ensure_public.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"GHCR packages are public"* ]]
}
