# scripts/deploy/doks_refresh_ghcr_pull_secret.sh — bats coverage

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/doks_refresh_ghcr_pull_secret.sh: requires token" {
  unset GH_TOKEN GITHUB_TOKEN || true
  run bash scripts/deploy/doks_refresh_ghcr_pull_secret.sh
  [ "$status" -eq 2 ]
}

@test "scripts/deploy/doks_refresh_ghcr_pull_secret.sh: dry-run apply with stub kubectl" {
  export GITHUB_TOKEN=test-token
  export GITHUB_ACTOR=test-actor
  export DOKS_NAMESPACE=metar-iwxxm-staging
  tmp="$(mktemp -d)"
  cat >"${tmp}/kubectl" <<'EOF'
#!/usr/bin/env bash
# Accept create --dry-run and apply -f -
if [[ "$*" == *"--dry-run=client"* ]]; then
  echo "apiVersion: v1"
  echo "kind: Secret"
  exit 0
fi
if [[ "$*" == *"apply"* ]]; then
  echo "secret/ghcr-pull configured"
  exit 0
fi
echo "unexpected kubectl args: $*" >&2
exit 1
EOF
  chmod +x "${tmp}/kubectl"
  PATH="${tmp}:$PATH" run bash scripts/deploy/doks_refresh_ghcr_pull_secret.sh
  [ "$status" -eq 0 ]
  [[ "$output" == *"Secret ghcr-pull applied"* ]]
}
