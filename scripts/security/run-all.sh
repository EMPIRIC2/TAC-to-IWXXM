#!/usr/bin/env bash
# Vendored portable security suite for CI (no ~/.cursor/skills). [Corpus: adr-037]
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
PREFIX="${SEC_TOOLS_DIR:-${HOME}/.local/share/security-static-analysis}"
BIN_DIR="${PREFIX}/bin"
ASSETS_DIR="${PREFIX}/assets"
REPORTS="${SEC_REPORTS_DIR:-${ROOT}/.security-reports}"
export PATH="${BIN_DIR}:${PATH}"
export REPORTS

log() { printf '[security] %s\n' "$*"; }
err() { printf '[security] ERROR: %s\n' "$*" >&2; }

mkdir -p "${REPORTS}"

if [[ "${SEC_INSTALL:-1}" == "1" ]]; then
  bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install-tools.sh"
fi

need() { command -v "$1" >/dev/null 2>&1 || { err "missing $1 — run scripts/security/install-tools.sh"; exit 1; }; }

fail=0
run() {
  local name="$1"; shift
  log "=== ${name} ==="
  set +e
  "$@"
  local c=$?
  set -e
  if [[ $c -ne 0 ]]; then
    err "${name} FAILED (exit ${c})"
    fail=1
    [[ "${SEC_FAIL_FAST:-1}" == "1" ]] && exit "$c"
  fi
}

need opengrep
need 2ms
need kics
need grype
need sbom-tool

# OpenGrep — write JSON; fail only on findings not in baseline (EV-049 migration).
BASELINE="${ROOT}/config/security/opengrep-baseline.txt"
FILTER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/filter-opengrep-baseline.py"
run_opengrep() {
  set +e
  # Redirect noisy JSON stdout; keep summary on stderr via tool itself
  opengrep scan --severity=ERROR --config="${SEC_OPENGREP_CONFIG:-p/default}" \
    --exclude=vendor --exclude=node_modules --exclude=.tools --exclude=.venv \
    --exclude=.security-reports --exclude=dist --exclude=build --exclude=target \
    --json --json-output="${REPORTS}/opengrep.json" "${ROOT}" >/dev/null
  local og_rc=$?
  set -e
  python3 "${FILTER}" "${REPORTS}/opengrep.json" "${BASELINE}" "${og_rc}" "${ROOT}"
}
run OpenGrep run_opengrep

run 2ms 2ms filesystem --path "${ROOT}" \
  --report-path "${REPORTS}/2ms.json" --report-path "${REPORTS}/2ms.sarif" \
  --max-target-megabytes 50 \
  --ignore-pattern 'node_modules' \
  --ignore-pattern '.venv' \
  --ignore-pattern 'target' \
  --ignore-pattern '.git' \
  --ignore-pattern '.security-reports' \
  --ignore-pattern '.tools' \
  --ignore-pattern 'dist' \
  --ignore-pattern 'package-lock.json' \
  --ignore-pattern '__pycache__' \
  --ignore-pattern '.pytest_cache' \
  --ignore-pattern 'htmlcov'

QUERIES="${ASSETS_DIR}/kics/assets/queries"
[[ -d "${QUERIES}" ]] || { err "KICS queries missing — run install-tools.sh"; exit 1; }
mkdir -p "${REPORTS}/kics"
run KICS kics scan -p "${ROOT}" -q "${QUERIES}" -o "${REPORTS}/kics" \
  --report-formats json,sarif --output-name results \
  --fail-on "${SEC_KICS_FAIL_ON:-high,critical}" \
  --exclude-paths ".git,.tools,.security-reports,.venv,node_modules,vendor,target,dist,build" \
  --exclude-gitignore

if [[ "${SEC_SKIP_SBOM:-0}" != "1" ]]; then
  DROP="${REPORTS}/sbom-drop"
  MOUT="${REPORTS}/sbom"
  rm -rf "${DROP}" "${MOUT}"
  mkdir -p "${DROP}" "${MOUT}"
  run SBOM sbom-tool generate -b "${DROP}" -bc "${ROOT}" -m "${MOUT}" \
    -pn "${SEC_SBOM_PACKAGE_NAME:-tac-to-iwxxm}" -pv "${SEC_SBOM_PACKAGE_VERSION:-0.0.0}" \
    -ps "${SEC_SBOM_PACKAGE_SUPPLIER:-EMPIRIC2}" -nsb "${SEC_SBOM_NAMESPACE:-https://github.com/EMPIRIC2/TAC-to-IWXXM}"
fi

SPDX="$(find "${REPORTS}/sbom" -type f -name '*.spdx.json' 2>/dev/null | head -1 || true)"
if [[ -n "${SPDX}" ]]; then
  TARGET="sbom:${SPDX}"
else
  TARGET="dir:${ROOT}"
fi
run Grype grype "${TARGET}" --fail-on "${SEC_GRYPE_FAIL_ON:-high}" -o json --file "${REPORTS}/grype.json" \
  --exclude=node_modules --exclude=vendor --exclude=.git --exclude=.venv --exclude=**/target

if [[ -f "${ROOT}/supabase/config.toml" || -n "${SUPABASE_PROJECT_REF:-}" || -n "${SUPABASE_URL:-}" ]]; then
  if [[ "${SEC_SKIP_SUPABASE_ADVISORS:-1}" == "1" ]]; then
    log "skipping Supabase advisors (SEC_SKIP_SUPABASE_ADVISORS=1)"
  elif [[ -f "${ROOT}/scripts/security/run-supabase-advisors.sh" ]]; then
    run "Supabase advisors" bash "${ROOT}/scripts/security/run-supabase-advisors.sh"
  else
    err "Supabase detected but advisors runner not configured"
    exit 1
  fi
else
  log "Supabase not detected — advisors N/A"
fi

if [[ "${fail}" -ne 0 ]]; then
  err "security suite failed — see ${REPORTS}"
  exit 1
fi
log "security suite passed — ${REPORTS}"
