#!/usr/bin/env bash
# Fail PRs to main unless head is stage and tip has a green Staging smoke run.
# Traces: F30 AC12 / TC-F30-012 / ADR-034 / #886
set -euo pipefail

REPO="${GITHUB_REPOSITORY:?}"
EVENT_NAME="${GITHUB_EVENT_NAME:?}"
BASE_REF="${GITHUB_BASE_REF:-}"
HEAD_REF="${GITHUB_HEAD_REF:-}"
SHA="${GITHUB_SHA:?}"
# Prefer PR head SHA when present
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

# Look for a successful workflow run on stage that includes this SHA and a Staging smoke job.
# Uses gh if available; else GitHub API via curl + GITHUB_TOKEN.
api() {
  local path="$1"
  curl -fsSL \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${GITHUB_TOKEN:?}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/${REPO}${path}"
}

# Check check-runs for this SHA for a successful "Staging smoke"
CHECKS_JSON="$(api "/commits/${SHA}/check-runs?per_page=100")"
python3 - <<'PY' "${CHECKS_JSON}"
import json, sys
data = json.loads(sys.argv[1])
runs = data.get("check_runs") or []
ok = [
    r for r in runs
    if r.get("name") == "Staging smoke"
    and r.get("status") == "completed"
    and r.get("conclusion") == "success"
]
if not ok:
    # Also accept workflow job name variants
    ok = [
        r for r in runs
        if "Staging smoke" in (r.get("name") or "")
        and r.get("status") == "completed"
        and r.get("conclusion") == "success"
    ]
if not ok:
    print("::error::No successful 'Staging smoke' check-run for this SHA. Merge to stage, wait for Deploy + Staging smoke, then open/update the PR.")
    sys.exit(1)
print(f"staging-gate: found {len(ok)} successful Staging smoke check-run(s)")
PY

# Defense in depth: probe staging health (HTTPS, else Host-header via LB)
API_URL="${STAGING_API_URL:-https://api.staging.tac-to-iwxxm.com}"
LB_IP="${DOKS_LB_IP:-168.144.12.70}"
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
