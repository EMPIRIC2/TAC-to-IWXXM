#!/usr/bin/env bash
# oasdiff OpenAPI contract gate (EV-quality-tooling-suite).
# [Corpus: api] [Corpus: tests]
#
# Two checks, both written to .quality-reports/ for the sticky PR comment:
#   1. breaking  - published spec (docs/api/openapi.json) vs the base branch copy.
#                  Fails the run when oasdiff reports changes at or above OASDIFF_FAIL_ON.
#   2. parity    - docs/api/openapi.json vs apps/frontend/openapi/openapi.json.
#                  The frontend copy must not drift from the published spec.
#
# Env (all optional):
#   OASDIFF_BIN           path to an oasdiff binary (skips lookup + install)
#   OASDIFF_VERSION       release to install when oasdiff is not on PATH (default below)
#   OASDIFF_INSTALL_DIR   install prefix (default ~/.local/share/oasdiff/bin)
#   OASDIFF_BASE          base spec file (overrides git base lookup)
#   OASDIFF_BASE_REF      git ref holding the base spec (default origin/$GITHUB_BASE_REF,
#                         then origin/stage, then origin/main)
#   OASDIFF_REVISION      revision spec file (default docs/api/openapi.json)
#   OASDIFF_FRONTEND_SPEC frontend copy (default apps/frontend/openapi/openapi.json)
#   OASDIFF_FAIL_ON       ERR (default) | WARN | NONE
#   OASDIFF_REQUIRE_BASE  1 = exit 2 when no base spec can be found (default: skip)
#   QUALITY_REPORTS_DIR   output directory (default .quality-reports)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

OASDIFF_VERSION="${OASDIFF_VERSION:-1.37.0}"
REVISION="${OASDIFF_REVISION:-docs/api/openapi.json}"
FRONTEND_SPEC="${OASDIFF_FRONTEND_SPEC:-apps/frontend/openapi/openapi.json}"
SPEC_PATH_IN_GIT="${OASDIFF_SPEC_GIT_PATH:-docs/api/openapi.json}"
FAIL_ON="${OASDIFF_FAIL_ON:-ERR}"
REPORT_DIR="${QUALITY_REPORTS_DIR:-.quality-reports}"
mkdir -p "${REPORT_DIR}"

log() { printf '[oasdiff] %s\n' "$*"; }
err() { printf '[oasdiff] ERROR: %s\n' "$*" >&2; }

case "${FAIL_ON}" in
  ERR | WARN | NONE) ;;
  *) err "OASDIFF_FAIL_ON must be ERR, WARN or NONE (got ${FAIL_ON})"; exit 2 ;;
esac

install_oasdiff() {
  local prefix="${OASDIFF_INSTALL_DIR:-${HOME}/.local/share/oasdiff/bin}"
  local os arch asset base_url tmp
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"
  arch="$(uname -m)"
  case "${os}" in
    linux)
      case "${arch}" in
        x86_64 | amd64) asset="oasdiff_${OASDIFF_VERSION}_linux_amd64.tar.gz" ;;
        aarch64 | arm64) asset="oasdiff_${OASDIFF_VERSION}_linux_arm64.tar.gz" ;;
        *) err "unsupported arch ${arch}"; exit 2 ;;
      esac
      ;;
    darwin) asset="oasdiff_${OASDIFF_VERSION}_darwin_all.tar.gz" ;;
    *) err "unsupported OS ${os}; use 'go install github.com/oasdiff/oasdiff@v${OASDIFF_VERSION}'"; exit 2 ;;
  esac
  base_url="https://github.com/oasdiff/oasdiff/releases/download/v${OASDIFF_VERSION}"
  tmp="$(mktemp -d)"
  log "installing oasdiff v${OASDIFF_VERSION} (${asset}) -> ${prefix}"
  curl -fsSL "${base_url}/${asset}" -o "${tmp}/${asset}"
  curl -fsSL "${base_url}/checksums.txt" -o "${tmp}/checksums.txt"
  local want got
  want="$(awk -v a="${asset}" '$2 == a { print $1 }' "${tmp}/checksums.txt")"
  if command -v sha256sum >/dev/null 2>&1; then
    got="$(sha256sum "${tmp}/${asset}" | awk '{ print $1 }')"
  else
    got="$(shasum -a 256 "${tmp}/${asset}" | awk '{ print $1 }')"
  fi
  if [[ -z "${want}" || "${want}" != "${got}" ]]; then
    err "checksum mismatch for ${asset} (want=${want:-none} got=${got})"
    exit 2
  fi
  mkdir -p "${prefix}"
  tar -xzf "${tmp}/${asset}" -C "${prefix}" oasdiff
  chmod +x "${prefix}/oasdiff"
  rm -rf "${tmp}"
  OASDIFF="${prefix}/oasdiff"
}

if [[ -n "${OASDIFF_BIN:-}" ]]; then
  OASDIFF="${OASDIFF_BIN}"
elif command -v oasdiff >/dev/null 2>&1; then
  OASDIFF="$(command -v oasdiff)"
else
  install_oasdiff
fi
OASDIFF_VERSION_STR="$("${OASDIFF}" --version 2>/dev/null | head -n1 || true)"
log "using ${OASDIFF} (${OASDIFF_VERSION_STR:-unknown version})"

if [[ ! -f "${REVISION}" ]]; then
  err "revision spec not found: ${REVISION}"
  exit 2
fi

# --- resolve base spec -------------------------------------------------------
BASE_FILE=""
BASE_LABEL=""
BASE_TMP=""
if [[ -n "${OASDIFF_BASE:-}" ]]; then
  BASE_FILE="${OASDIFF_BASE}"
  BASE_LABEL="${OASDIFF_BASE}"
else
  candidates=()
  [[ -n "${OASDIFF_BASE_REF:-}" ]] && candidates+=("${OASDIFF_BASE_REF}")
  [[ -n "${GITHUB_BASE_REF:-}" ]] && candidates+=("origin/${GITHUB_BASE_REF}")
  candidates+=("origin/stage" "origin/main")
  for ref in "${candidates[@]}"; do
    if git rev-parse --verify --quiet "${ref}^{commit}" >/dev/null 2>&1 \
      && git cat-file -e "${ref}:${SPEC_PATH_IN_GIT}" 2>/dev/null; then
      BASE_TMP="$(mktemp -d)"
      BASE_FILE="${BASE_TMP}/openapi.base.json"
      git show "${ref}:${SPEC_PATH_IN_GIT}" >"${BASE_FILE}"
      BASE_LABEL="${ref}:${SPEC_PATH_IN_GIT}"
      break
    fi
  done
fi
cleanup() { [[ -n "${BASE_TMP}" ]] && rm -rf "${BASE_TMP}"; return 0; }
trap cleanup EXIT

BREAKING_STATUS="skipped"
BREAKING_RC=0
if [[ -z "${BASE_FILE}" || ! -f "${BASE_FILE}" ]]; then
  if [[ "${OASDIFF_REQUIRE_BASE:-0}" == "1" ]]; then
    err "no base spec found (set OASDIFF_BASE or OASDIFF_BASE_REF)"
    exit 2
  fi
  log "no base spec found; breaking-change check skipped"
  : >"${REPORT_DIR}/oasdiff-breaking.txt"
  printf '[]\n' >"${REPORT_DIR}/oasdiff-breaking.json"
else
  log "breaking: ${BASE_LABEL} -> ${REVISION} (fail-on=${FAIL_ON})"
  "${OASDIFF}" breaking "${BASE_FILE}" "${REVISION}" -f json >"${REPORT_DIR}/oasdiff-breaking.json" || true
  fail_args=()
  [[ "${FAIL_ON}" != "NONE" ]] && fail_args+=(--fail-on "${FAIL_ON}")
  set +e
  "${OASDIFF}" breaking "${BASE_FILE}" "${REVISION}" -f text ${fail_args[@]+"${fail_args[@]}"} \
    >"${REPORT_DIR}/oasdiff-breaking.txt" 2>&1
  BREAKING_RC=$?
  set -e
  if [[ "${BREAKING_RC}" -eq 0 ]]; then BREAKING_STATUS="pass"; else BREAKING_STATUS="fail"; fi
  cat "${REPORT_DIR}/oasdiff-breaking.txt"
fi

# --- frontend copy parity ----------------------------------------------------
PARITY_STATUS="skipped"
PARITY_RC=0
if [[ -f "${FRONTEND_SPEC}" ]]; then
  log "parity: ${REVISION} vs ${FRONTEND_SPEC}"
  set +e
  "${OASDIFF}" diff "${REVISION}" "${FRONTEND_SPEC}" --fail-on-diff -f text \
    >"${REPORT_DIR}/oasdiff-parity.txt" 2>&1
  PARITY_RC=$?
  set -e
  if [[ "${PARITY_RC}" -eq 0 ]]; then PARITY_STATUS="pass"; else PARITY_STATUS="fail"; fi
  cat "${REPORT_DIR}/oasdiff-parity.txt"
else
  log "frontend spec ${FRONTEND_SPEC} missing; parity check skipped"
  : >"${REPORT_DIR}/oasdiff-parity.txt"
fi

# --- summary (json + markdown) ----------------------------------------------
OASDIFF_SUMMARY_BASE="${BASE_LABEL}" \
OASDIFF_SUMMARY_REVISION="${REVISION}" \
OASDIFF_SUMMARY_FRONTEND="${FRONTEND_SPEC}" \
OASDIFF_SUMMARY_VERSION="${OASDIFF_VERSION_STR}" \
OASDIFF_SUMMARY_FAIL_ON="${FAIL_ON}" \
OASDIFF_SUMMARY_BREAKING="${BREAKING_STATUS}" \
OASDIFF_SUMMARY_PARITY="${PARITY_STATUS}" \
python3 - "${REPORT_DIR}" <<'PY'
import json
import os
import sys
from pathlib import Path

out = Path(sys.argv[1])
env = os.environ
try:
    findings = json.loads((out / "oasdiff-breaking.json").read_text(encoding="utf-8") or "[]")
except json.JSONDecodeError:
    findings = []
if not isinstance(findings, list):
    findings = []
levels = {1: "info", 2: "warning", 3: "error"}
counts = {"error": 0, "warning": 0, "info": 0}
rows = []
for f in findings:
    lvl = levels.get(f.get("level"), "info")
    counts[lvl] += 1
    rows.append(
        {
            "level": lvl,
            "id": f.get("id", ""),
            "operation": f.get("operation", ""),
            "path": f.get("path", ""),
            "text": f.get("text", ""),
        }
    )
summary = {
    "tool": "oasdiff",
    "version": env["OASDIFF_SUMMARY_VERSION"],
    "base": env["OASDIFF_SUMMARY_BASE"],
    "revision": env["OASDIFF_SUMMARY_REVISION"],
    "frontend_copy": env["OASDIFF_SUMMARY_FRONTEND"],
    "fail_on": env["OASDIFF_SUMMARY_FAIL_ON"],
    "breaking": {"status": env["OASDIFF_SUMMARY_BREAKING"], **counts, "findings": rows},
    "parity": {"status": env["OASDIFF_SUMMARY_PARITY"]},
}
summary["status"] = (
    "fail"
    if "fail" in (summary["breaking"]["status"], summary["parity"]["status"])
    else "pass"
)
(out / "oasdiff.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

icon = {"pass": "PASS", "fail": "FAIL", "skipped": "SKIPPED"}
lines = [
    "### oasdiff",
    "",
    f"- Overall: **{icon[summary['status']]}** (`fail-on={summary['fail_on']}`)",
    f"- Breaking vs base: **{icon[summary['breaking']['status']]}** "
    f"({counts['error']} error, {counts['warning']} warning, {counts['info']} info)"
    + (f" - base `{summary['base']}`" if summary["base"] else ""),
    f"- Frontend copy parity: **{icon[summary['parity']['status']]}** "
    f"(`{summary['revision']}` vs `{summary['frontend_copy']}`)",
]
if rows:
    lines += ["", "| Level | Operation | Change |", "|---|---|---|"]
    for r in rows[:25]:
        op = f"{r['operation']} {r['path']}".strip()
        lines.append(f"| {r['level']} | `{op}` | {r['text']} |")
    if len(rows) > 25:
        lines.append(f"| ... | | {len(rows) - 25} more in `oasdiff-breaking.txt` |")
(out / "oasdiff.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

log "reports: ${REPORT_DIR}/oasdiff.md ${REPORT_DIR}/oasdiff.json"

if [[ "${BREAKING_RC}" -ne 0 || "${PARITY_RC}" -ne 0 ]]; then
  err "contract check failed (breaking=${BREAKING_STATUS} parity=${PARITY_STATUS})"
  exit 1
fi
log "oasdiff green"
