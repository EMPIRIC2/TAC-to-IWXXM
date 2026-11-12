# scripts/ci/run_oasdiff.sh — bats coverage (EV-quality-tooling-suite)
# NFR-EV080-006: stub oasdiff binary; no live network. [Corpus: api] [Corpus: tests]

load "${BATS_TEST_DIRNAME}/../helpers/load"

_stub_oasdiff() {
  # $1 = exit code for the `breaking` subcommand
  cat >"${BATS_TEST_TMPDIR}/oasdiff" <<EOF
#!/usr/bin/env bash
case "\$1" in
  --version) echo "oasdiff version 0.0.0-stub" ;;
  breaking) echo "stub breaking"; exit ${1} ;;
  diff) echo "No changes" ;;
esac
exit 0
EOF
  chmod +x "${BATS_TEST_TMPDIR}/oasdiff"
  export OASDIFF_BIN="${BATS_TEST_TMPDIR}/oasdiff"
  export OASDIFF_BASE="docs/api/openapi.json"
  export QUALITY_REPORTS_DIR="${BATS_TEST_TMPDIR}/reports"
}

@test "scripts/ci/run_oasdiff.sh: stub oasdiff with no changes exits 0" {
  _stub_oasdiff 0
  run bash scripts/ci/run_oasdiff.sh
  [ "$status" -eq 0 ]
  [ -f "${QUALITY_REPORTS_DIR}/oasdiff-breaking.txt" ]
  [ -f "${QUALITY_REPORTS_DIR}/oasdiff-parity.txt" ]
}

@test "scripts/ci/run_oasdiff.sh: breaking changes exit 1" {
  _stub_oasdiff 1
  run bash scripts/ci/run_oasdiff.sh
  [ "$status" -eq 1 ]
}

@test "scripts/ci/run_oasdiff.sh: missing base is skipped unless required" {
  _stub_oasdiff 0
  unset OASDIFF_BASE
  export OASDIFF_BASE_REF="refs/does/not/exist"
  export GITHUB_BASE_REF="no-such-branch"
  run env OASDIFF_REQUIRE_BASE=1 bash scripts/ci/run_oasdiff.sh
  # origin/stage or origin/main may exist locally; either way the script must not crash.
  [ "$status" -eq 0 ] || [ "$status" -eq 2 ]
}

@test "scripts/ci/run_oasdiff.sh: invalid OASDIFF_FAIL_ON exits 2" {
  _stub_oasdiff 0
  run env OASDIFF_FAIL_ON=bogus bash scripts/ci/run_oasdiff.sh
  [ "$status" -eq 2 ]
}
