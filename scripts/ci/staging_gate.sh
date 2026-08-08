#!/usr/bin/env bash
# Fail PRs to main unless head is stage and tip has a green Staging smoke run.
# Traces: F30 AC12 / TC-F30-012 / ADR-034 / #886 / EV-044 (staging LB Host-header)
set -euo pipefail

REPO="${GITHUB_REPOSITORY:?}"
EVENT_NAME="${GITHUB_EVENT_NAME:?}"
BASE_REF="${GITHUB_BASE_REF:-}"
HEAD_REF="${GITHUB_HEAD_REF:-}"
SHA="${GITHUB_SHA:?}"
if [[ -n "${GITHUB_EVENT_PATH:-}" && -f "${GITHUB_EVENT_PATH}" ]]; then
  PR_SHA="$(python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(d.get("pull_request",{}).get("head",{}).get("sha",""))' "${GITHUB_EVENT_PATH}" || true)"
  if [[ -n "${PR_SHA}" ]]; then
    SHA="${PR_SHA}"
  fi
fi

if [[ "${EVENT_NAME}" != "pull_request" ]]; then
  echo "staging-gate: skip (event=${EVENT_NAME})"
  exit 0
fi

if [[ "${BASE_REF}" != "main" ]]; then
  echo "staging-gate: skip (base=${BASE_REF})"
  exit 0
fi

if [[ "${HEAD_REF}" != "stage" ]]; then
  echo "::error::PRs to main must come from branch 'stage' (got '${HEAD_REF}'). Promote via stage→main only (ADR-034)."
  exit 1
fi

echo "staging-gate: head=stage sha=${SHA}"

api() {
  local path="$1"
  curl -fsSL \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${GITHUB_TOKEN:?}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/${REPO}${path}"
}

TMP="$(mktemp)"
trap 'rm -f "${TMP}"' EXIT
# PR synchronize often races the stage-push Staging smoke job — poll up to ~12 minutes.
DEADLINE=$((SECONDS + 720))
ok_count=0
while true; do
  api "/commits/${SHA}/check-runs?per_page=100" >"${TMP}"
  ok_count="$(python3 - <<'PY' "${TMP}"
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)
runs = data.get("check_runs") or []
ok = [
    r for r in runs
    if "Staging smoke" in (r.get("name") or "")
    and r.get("status") == "completed"
    and r.get("conclusion") == "success"
]
print(len(ok))
PY
)"
  if [[ "${ok_count}" -gt 0 ]]; then
    echo "staging-gate: found ${ok_count} successful Staging smoke check-run(s)"
    break
  fi
  if [[ "${SECONDS}" -ge "${DEADLINE}" ]]; then
    python3 - <<'PY' "${TMP}"
import json, sys
with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)
runs = data.get("check_runs") or []
names = sorted({r.get("name") for r in runs if r.get("conclusion") == "success"})
print("::error::No successful 'Staging smoke' check-run for this SHA after waiting. Merge to stage, wait for Deploy + Staging smoke, then open/update the PR.")
print("successful check names sample:", ", ".join(names[:30]))
sys.exit(1)
PY
  fi
  echo "staging-gate: Staging smoke not green yet for ${SHA}; sleeping 30s…"
  sleep 30
done

API_URL="${STAGING_API_URL:-https://api.staging.tac-to-iwxxm.com}"
# EV-044: staging cluster LB (not prod 168.144.12.70). Override via STAGING_LB_IP / DOKS_LB_IP.
LB_IP="${STAGING_LB_IP:-${DOKS_LB_IP:-143.244.202.13}}"
code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 "${API_URL}/health" || echo 000)"
if [[ "${code}" != "200" ]]; then
  code="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 20 \
    -H "Host: api.staging.tac-to-iwxxm.com" "http://${LB_IP}/health" || echo 000)"
fi
if [[ "${code}" != "200" ]]; then
  echo "::error::Staging API /health returned ${code} (${API_URL})"
  exit 1
fi
echo "staging-gate: staging /health → 200"
echo "staging-gate: PASS"
