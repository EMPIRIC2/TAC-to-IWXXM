# Shared bats setup for scripts/**/*.sh (EV-080 / ADR-007).
# NFR-EV080-006: stub external CLIs — no live network or cloud credentials.

bats_load_helpers() {
  # shellcheck disable=SC2034
  BATS_HELPERS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  _d="${BATS_TEST_DIRNAME}"
  while [[ "$(basename "${_d}")" != "bats" && "${_d}" != "/" ]]; do
    _d="$(cd "${_d}/.." && pwd)"
  done
  if [[ "$(basename "${_d}")" == "bats" ]]; then
    # shellcheck disable=SC2034
    REPO_ROOT="$(cd "${_d}/../.." && pwd)"
    BATS_HELPERS_DIR="$(cd "${_d}/helpers" && pwd)"
  else
    # shellcheck disable=SC2034
    REPO_ROOT="$(cd "${BATS_HELPERS_DIR}/../../.." && pwd)"
  fi
  export REPO_ROOT
  export PATH="${BATS_HELPERS_DIR}/bin:${PATH}"
  export UV="${BATS_HELPERS_DIR}/bin/uv"
  export BATS_MOCK=1
}

bats_load_helpers

setup() {
  cd "${REPO_ROOT}" || return 1
}

setup_file() {
  cd "${REPO_ROOT}" || return 1
}
