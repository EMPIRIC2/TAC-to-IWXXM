#!/usr/bin/env bash
# Apply GitHub rulesets for stage + main (requires repo admin).
# Traces: F30 AC11 / TC-F30-011 / ADR-034 / #886
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-EMPIRIC2/TAC-to-IWXXM}"

create_ruleset() {
  local name="$1"
  local pattern="$2"
  local extra_checks_json="$3"
  local body
  body="$(python3 - <<PY
import json
# Job `name:` strings from .github/workflows/ci-cd.yml (must match exactly).
# EV-045 / #725 / TC-EV045-006 — Rust crates + both maturin smokes.
checks = [
    {"context": "Test (backend)", "integration_id": 0},
    {"context": "Test (frontend)", "integration_id": 0},
    {"context": "Alembic migrations", "integration_id": 0},
    {"context": "Rust crates (fmt/clippy/test)", "integration_id": 0},
    {"context": "tac2iwxxm PyO3 (maturin)", "integration_id": 0},
    {"context": "iwxxm-validate PyO3 (maturin)", "integration_id": 0},
]
extra = json.loads('''${extra_checks_json}''')
checks.extend(extra)
print(json.dumps({
  "name": "${name}",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["${pattern}"], "exclude": []}},
  "rules": [
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": False,
      "require_code_owner_review": False,
      "require_last_push_approval": False,
      "required_review_thread_resolution": False,
    }},
    {"type": "non_fast_forward"},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": True,
      "do_not_enforce_on_create": True,
      "required_status_checks": checks,
    }},
  ],
}))
PY
)"
  echo "Creating/updating ruleset ${name} for ${pattern}"
  gh api --method POST "repos/${REPO}/rulesets" --input - <<<"${body}" \
    || echo "::warning::ruleset ${name} create failed (need admin). See docs/ops/doks-staging-dns-runbook.md"
}

create_ruleset "protect-stage" "refs/heads/stage" "[]"
create_ruleset "protect-main" "refs/heads/main" '[{"context":"Staging gate","integration_id":0}]'

echo "Done. Also create Environments staging + production (no reviewers) in GitHub Settings."
