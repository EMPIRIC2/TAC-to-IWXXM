# 09-qa — S063 / EV-054

**Date:** 2026-08-10  
**Verdict:** **PASS** (advisories below)  
**Tip:** `be9e3b07` · branch `evolve/EV-054-quality-metrics-tab` (no open PR → `stage` yet)  
**Corpus:** [Corpus: product §F7] [Corpus: api] [Corpus: journeys §UJ-056] [Corpus: tests]

```text
QA Results:
  Lint:           PASS — 0 issues (make lint-fast)
  Format:         PASS — 0 files (make format-check)
  Typecheck:      PASS — 0 errors (make validate-fast / basedpyright + tsc)
  Tests (Python): PASS — 1339 passed (make test-unit-backend); H0c 6/6
  Tests (FE):     PASS — 1011 passed | 4 skipped (98 files); branches 95.1%
  Security:       PASS — gitleaks tree PASS; pip-audit 0 known (uv export + uvx)
  Cross-file:     PASS — no blocking pickle/eval/exec in apps|packages (regex .exec OK)
  Dependencies:   PASS — pip-audit clean; FE audit deferred to CI medium
  Template:       PASS — apps/* + packages/* + vendor/schemas
  Data / Modal:   N/A for this delta (no Modal deploy in EV-054)
```

## Checks

| ID | Check | Result |
|----|-------|--------|
| QA-001 | Lint / format (`make lint-fast`, `format-check`) | PASS |
| QA-002 | Typecheck + validate-fast (secrets, yaml, actionlint, catalog) | PASS |
| QA-003 | Backend unit `make test-unit-backend` | PASS — 1339; coverage 98.35%; per-file ≥95% |
| QA-004 | Frontend unit `make test-unit-frontend` | PASS — 1011 passed; stmts 98.28 / branches **95.1** / lines 98.71 |
| QA-005 | H0c CORS `tests/unit/test_cors_policy.py` | PASS (6) |
| QA-006 | H0i `tests/integration` | PASS exit 0 — 10 skipped (no live stack) |
| QA-007 | Secrets `make secrets-check` / gitleaks pre-commit | PASS |
| QA-008 | pip-audit (`uv export --frozen --no-dev` + `uvx pip-audit --no-deps`) | PASS (0 known) |
| QA-009 | Template layout | PASS |
| QA-010 | Connectivity artifacts (`tests/smoke/test_staging_connectivity.py`, `scripts/deploy/verify_connectivity.sh`) | PASS present |
| QA-011 | Tip CI @ `be9e3b07` | **PENDING** — no open PR → stage |
| QA-012 | H4–H5 live staging | SKIPPED → 12/13 |

## AC map (delta — EV-054 / F7.q)

| AC | Status | Evidence |
|----|--------|----------|
| AC1 | PASS | Shell tab + list/filter — TC-EV054-001..002; Vitest |
| AC2 | PASS | Unified XML diff — TC-EV054-003 |
| AC3 | PASS | Residuals / lint / validate panes — TC-EV054-004 |
| AC4 | PASS | Precomputed fixture + generator — TC-EV054-005 |
| AC5 | PASS | Gap stems labeled — TC-EV054-002 |
| AC6 | PASS (local) | Playwright UJ-056 TC-EV054-007 — see `e2e-report.md`; live H4–H5 → 12/13 |
| AC7 | PASS | Offline public GET `/api/v1/quality-metrics*` — TC-EV054-006/008 |

## Advisories

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-ADV-001 | advisory | Tip CI not watched — no open PR for `evolve/EV-054-quality-metrics-tab` → `stage` | Open PR before or during 11/12; watch `ci.yml` |
| QA-ADV-002 | advisory | H0i integration suite skipped locally (env-gated) | Rely on CI Integration Matrix |
| QA-ADV-003 | advisory | Live H4–H5 staging smoke not run in 09 | Stages 12/13 after merge to stage |
| QA-ADV-004 | advisory | basedpyright warnings in `packages/auth` / `tac2iwxxm` (pre-existing Unknown) | Out of EV-054 scope unless 11 expands |

## Commands (repro)

```bash
make lint-fast
make format-check
make validate-fast
make test-unit-backend
make test-unit-frontend
uv run pytest tests/unit/test_cors_policy.py -q
uv run pytest tests/integration -q
uv export --frozen --no-dev -o /tmp/req-audit.txt && uvx pip-audit -r /tmp/req-audit.txt --no-deps
```

## Exit

→ **10-e2e** (parallel) then **11-verify-impl**
