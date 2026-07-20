# QA Report — S018 / EV-013 (#667 remarks)

> Generated: 2026-07-20  
> Branch: `cursor/metar-remarks-667-tests-1fe0` (includes feat #750 tip + TC-F6-013 expansion)  
> Mode: **delta** (F6 deepen / EV-013)  
> Overall: **PASS** (one advisory FE flake under concurrent load)

```text
QA Results:
  Lint:           PASS — 0 issues
  Format:         PASS — 0 files
  Typecheck:      PASS — 0 errors (py + js)
  Tests (Python): PASS — see table (CI-style make targets)
  Tests (FE):     PASS — 644 / 644 on clean re-run (2 timeouts under concurrent load; advisory)
  Security:       PASS — gitleaks --no-git: no leaks; pip-audit: no known vulns
  H0c CORS:       PASS — 6 passed (tests/unit/test_cors_policy.py)
  H0i:            PASS — 10 passed (apps/backend integration, --no-cov)
  Cross-file:     PASS — ruff clean on apps/packages/tests
  Template:       PASS — no layout drift in this delta
  Staging H4–H5:  ADVISORY — deferred to 13-deploy-smoke
```

## Executive summary

| Check | Result | Notes |
|-------|--------|-------|
| Format | PASS | `make format-check` |
| Lint | PASS | `make lint` |
| Typecheck | PASS | `make typecheck` |
| tac2iwxxm | PASS | 171 passed, 9 skipped (≥95% cov) |
| tac-validate | PASS | 296 passed |
| iwxxm-validate | PASS | 76 passed, 1 skipped |
| backend unit | PASS | 1216 passed |
| auth | PASS | 228 passed, 31 skipped |
| shared / workspace | PASS | 76 + 44 passed |
| worker | PASS | 11 passed |
| bugs | PASS | 44 passed, 1 deselected |
| frontend | PASS | 644 passed (re-run); see QA-001 |
| H0c | PASS | blocking connectivity |
| H0i | PASS | blocking connectivity |
| Security tree | PASS | gitleaks no-git; pip-audit clean |

## Commands run (reproducible)

```bash
make format-check
make lint
make typecheck
make test-unit-tac2iwxxm
make test-unit-tac-validate
make test-unit-iwxxm-validate
make test-unit-backend
make test-unit-auth
make test-unit-shared-py
make test-unit-workspace-py
make test-unit-worker
make test-bugs
make test-unit-frontend   # clean re-run after flake
uv run pytest tests/unit/test_cors_policy.py -q
cd apps/backend && uv run pytest tests/integration/test_h0i_connectivity.py -q --no-cov
gitleaks detect --no-git --config .gitleaks.toml
uv run pip-audit
```

**Note:** Do not collect multiple packages in one root `pytest` invocation — basename collisions
(`test_issue_spans`, `test_native_scaffold`) cause import-file mismatches. Use Make targets / CI jobs.

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | Advisory | First `make test-unit-frontend` under concurrent QA load: 2 Vitest timeouts (`bug-2026-07-12-result-card-dismiss`, `FileConverter` row remove). Isolated + full re-run: **644/644 PASS**. | Treat as load flake; no code change required for EV-013. Optional: raise testTimeout on those two cases. |
| QA-002 | Advisory | Staging H4–H5 not run in this 09 pass. | 13-deploy-smoke after merge of #750/#751. |
| QA-003 | Advisory | `scripts/check_secrets.sh` not present; used gitleaks `--no-git` instead. | None for this cycle. |

## Phase / plan alignment

- EV-013 implementation + TC-F6-013 expansion covered by local suite + CI green on `cursor/metar-remarks-667-2e2e` ([run](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29773115125)).
- Related PRs: [#750](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/750) (feat), [#751](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/751) (test expansion).
