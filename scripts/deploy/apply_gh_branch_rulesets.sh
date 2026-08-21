#!/usr/bin/env bash
# Apply GitHub rulesets for stage + main (requires repo admin).
# Traces: F30 AC11 / TC-F30-011 / ADR-034 / #886
# EV-061 / #1015 / TC-EV061-1015 / D-S071-ci — stricter stage→main required checks.
set -euo pipefail

REPO="${GITHUB_REPOSITORY:-EMPIRIC2/TAC-to-IWXXM}"

create_ruleset() {
  local name="$1"
  local pattern="$2"
  local extra_checks_json="$3"
  local body
  body="$(python3 - <<PY
import json
# Job name: strings from .github/workflows/ci-cd.yml (must match exactly).
# EV-045 / #725 / TC-EV045-006 — Rust crates + both maturin smokes.
# EV-047 / #834 / TC-EV047-007 — converter perf hard gate (D-S056-gateA=2).
# EV-061 / #1015 / TC-EV061-1015 — full Test (*), Lint, Typecheck; main + E2E Full + Staging gate.
# NOTE: do not use shell backticks in this heredoc (they expand before python).
checks = [
    {"context": "Test (shared)", "integration_id": 0},
    {"context": "Test (auth)", "integration_id": 0},
    {"context": "Test (backend)", "integration_id": 0},
    {"context": "Test (frontend)", "integration_id": 0},
    {"context": "Test (tac2iwxxm)", "integration_id": 0},
    {"context": "Test (iwxxm-validate)", "integration_id": 0},
    {"context": "Test (tac-validate)", "integration_id": 0},
    {"context": "Test (dissemination)", "integration_id": 0},
    {"context": "Test (worker)", "integration_id": 0},
    {"context": "Test (bugs)", "integration_id": 0},
    {"context": "Test (alembic / TC-EV031-002)", "integration_id": 0},
    {"context": "Lint", "integration_id": 0},
    {"context": "Typecheck", "integration_id": 0},
    {"context": "Rust crates (fmt/clippy/test)", "integration_id": 0},
    {"context": "tac2iwxxm PyO3 (maturin)", "integration_id": 0},
    {"context": "iwxxm-validate PyO3 (maturin)", "integration_id": 0},
    {"context": "Converter perf (tac2iwxxm)", "integration_id": 0},
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
  # Prefer create; if name exists, PATCH by id.
  if ! gh api --method POST "repos/${REPO}/rulesets" --input - <<<"${body}"; then
    existing_id="$(gh api "repos/${REPO}/rulesets" --jq ".[] | select(.name==\"${name}\") | .id" 2>/dev/null || true)"
    if [[ -n "${existing_id}" ]]; then
      echo "Ruleset ${name} exists (id=${existing_id}); updating"
      gh api --method PUT "repos/${REPO}/rulesets/${existing_id}" --input - <<<"${body}" \
        || echo "::warning::ruleset ${name} update failed (need admin)."
    else
      echo "::warning::ruleset ${name} create failed (need admin). See docs/ops/doks-staging-dns-runbook.md"
    fi
  fi
}

create_ruleset "protect-stage" "refs/heads/stage" "[]"
# Main-only: Staging gate + full Playwright (not smoke-only). E2E Full job runs only on
# PRs targeting main (see ci-cd.yml e2e-full if:).
create_ruleset "protect-main" "refs/heads/main" '[{"context":"Staging gate","integration_id":0},{"context":"E2E Full (Playwright)","integration_id":0}]'

echo "Done. Also create Environments staging + production (no reviewers) in GitHub Settings."
