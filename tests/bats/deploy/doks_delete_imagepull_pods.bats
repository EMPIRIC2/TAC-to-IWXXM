# scripts/deploy/doks_delete_imagepull_pods.sh — bats coverage
# NFR: stub kubectl/python; no live cluster.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/deploy/doks_delete_imagepull_pods.sh: no-op when no stuck pods" {
  tmp="$(mktemp -d)"
  cat >"${tmp}/kubectl" <<'EOF'
#!/usr/bin/env bash
if [[ "$*" == *get*pods* ]]; then
  echo '{"items":[]}'
  exit 0
fi
echo "unexpected kubectl $*" >&2
exit 1
EOF
  chmod +x "${tmp}/kubectl"
  PATH="${tmp}:$PATH" DOKS_NAMESPACE=metar-iwxxm-staging \
    run bash scripts/deploy/doks_delete_imagepull_pods.sh
  [ "$status" -eq 0 ]
}
