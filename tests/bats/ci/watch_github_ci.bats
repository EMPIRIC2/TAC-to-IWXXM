# scripts/ci/watch_github_ci.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub gh and sleep; no live network or GitHub auth.

load "${BATS_TEST_DIRNAME}/../helpers/load"

setup() {
  bats_load_helpers
  cd "${REPO_ROOT}" || return 1
  export TMPDIR_FOR_TEST="$(mktemp -d)"
  export GH_BIN="${TMPDIR_FOR_TEST}/gh"
  export SLEEP_BIN="${TMPDIR_FOR_TEST}/sleep"
  export GH_STATE_FILE="${TMPDIR_FOR_TEST}/gh-state"
  : >"${GH_STATE_FILE}"

  cat >"${SLEEP_BIN}" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
  chmod +x "${SLEEP_BIN}"
}

teardown() {
  rm -rf "${TMPDIR_FOR_TEST}"
}

@test "scripts/ci/watch_github_ci.sh: usage when target missing" {
  run bash scripts/ci/watch_github_ci.sh
  [ "$status" -eq 2 ]
}

@test "scripts/ci/watch_github_ci.sh: passes when checks are green" {
  cat >"${GH_BIN}" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
case "$1 $2" in
  "pr checks")
    printf 'Lint\tpass\t54s\thttps://example.test/lint\n'
    ;;
  *)
    echo "unexpected args: $*" >&2
    exit 99
    ;;
esac
EOF
  chmod +x "${GH_BIN}"

  run bash -c '
    export GH_BIN="$1"
    export SLEEP_BIN="$2"
    export CI_WATCH_POLL_SEC=0
    export CI_WATCH_TIMEOUT_SEC=10
    bash scripts/ci/watch_github_ci.sh 1150
  ' _ "${GH_BIN}" "${SLEEP_BIN}"
  [ "$status" -eq 0 ]
  [[ "$output" == *"target=1150 pr=1150"* ]]
  [[ "$output" == *"watch_github_ci: PASS"* ]]
}

@test "scripts/ci/watch_github_ci.sh: fails closed on check failure" {
  cat >"${GH_BIN}" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
case "$1 $2" in
  "pr checks")
    printf 'Test (frontend)\tfail\t3m26s\thttps://example.test/frontend\n'
    exit 1
    ;;
  *)
    echo "unexpected args: $*" >&2
    exit 99
    ;;
esac
EOF
  chmod +x "${GH_BIN}"

  run bash -c '
    export GH_BIN="$1"
    export SLEEP_BIN="$2"
    export CI_WATCH_POLL_SEC=0
    export CI_WATCH_TIMEOUT_SEC=10
    bash scripts/ci/watch_github_ci.sh 1150
  ' _ "${GH_BIN}" "${SLEEP_BIN}"
  [ "$status" -eq 1 ]
  [[ "$output" == *"checks failed for PR 1150"* ]]
}
