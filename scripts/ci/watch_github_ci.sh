#!/usr/bin/env bash
# Watch GitHub PR checks without relying on gh's --watch GraphQL loop.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "${ROOT}"

TARGET="${1:-}"
POLL_SEC="${CI_WATCH_POLL_SEC:-15}"
TIMEOUT_SEC="${CI_WATCH_TIMEOUT_SEC:-1800}"
GH_BIN="${GH_BIN:-gh}"
SLEEP_BIN="${SLEEP_BIN:-sleep}"

if [[ -z "${TARGET}" ]]; then
  echo "Usage: $0 <pr-number|head-branch>" >&2
  exit 2
fi

if ! [[ "${POLL_SEC}" =~ ^[0-9]+$ && "${TIMEOUT_SEC}" =~ ^[0-9]+$ ]]; then
  echo "watch_github_ci: CI_WATCH_POLL_SEC and CI_WATCH_TIMEOUT_SEC must be integers" >&2
  exit 2
fi

resolve_pr_number() {
  if [[ "${TARGET}" =~ ^[0-9]+$ ]]; then
    printf '%s\n' "${TARGET}"
    return 0
  fi

  local pr_number
  pr_number="$("${GH_BIN}" pr list --state open --head "${TARGET}" --json number --jq '.[0].number // ""')"
  if [[ -z "${pr_number}" ]]; then
    echo "watch_github_ci: no open PR found for head branch '${TARGET}'" >&2
    exit 1
  fi
  printf '%s\n' "${pr_number}"
}

is_transient_gh_error() {
  local output="$1"
  [[ "${output}" == *"no checks reported on the"* ]] ||
    [[ "${output}" == *"Post \"https://api.github.com/graphql\""* ]] ||
    [[ "${output}" == *"can't assign requested address"* ]] ||
    [[ "${output}" == *"connection reset by peer"* ]] ||
    [[ "${output}" == *"unexpected EOF"* ]]
}

has_failed_checks() {
  local output="$1"
  printf '%s\n' "${output}" | python3 -c '
import sys

bad = {"fail", "failing", "cancel", "cancelled", "timed_out", "timed out", "startup_failure"}
for raw_line in sys.stdin:
    parts = [part.strip().lower() for part in raw_line.split("\t")]
    if len(parts) >= 2 and parts[1] in bad:
        raise SystemExit(0)
raise SystemExit(1)
'
}

PR_NUMBER="$(resolve_pr_number)"
echo "watch_github_ci: target=${TARGET} pr=${PR_NUMBER} poll=${POLL_SEC}s timeout=${TIMEOUT_SEC}s"

deadline=$((SECONDS + TIMEOUT_SEC))
while true; do
  set +e
  OUTPUT="$("${GH_BIN}" pr checks "${PR_NUMBER}" 2>&1)"
  RC=$?
  set -e

  printf '%s\n' "${OUTPUT}"

  if [[ "${RC}" -eq 0 ]]; then
    echo "watch_github_ci: PASS"
    exit 0
  fi

  if has_failed_checks "${OUTPUT}"; then
    echo "::error::watch_github_ci: checks failed for PR ${PR_NUMBER}" >&2
    exit 1
  fi

  if [[ "${RC}" -eq 8 ]] || is_transient_gh_error "${OUTPUT}"; then
    if [[ "${SECONDS}" -ge "${deadline}" ]]; then
      echo "::error::watch_github_ci: timed out waiting for checks on PR ${PR_NUMBER}" >&2
      exit 1
    fi
    echo "watch_github_ci: checks not settled yet; retrying in ${POLL_SEC}s" >&2
    "${SLEEP_BIN}" "${POLL_SEC}"
    continue
  fi

  echo "::error::watch_github_ci: gh pr checks exited ${RC} for PR ${PR_NUMBER}" >&2
  exit "${RC}"
done
