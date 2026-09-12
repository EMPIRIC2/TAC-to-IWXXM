# QA Report — S056 / EV-047 (09-qa)

> Generated: 2026-08-08  
> Scope: delta — deepen M5 (husky) + F6 (converter perf) + F7 (Help/docs) + coverage 95%  
> Branch: `evolve/EV-047-m0-stabilize-operator-trust` @ `3ca4f438`  
> Mode: delta  
> Corpus: [Corpus: product §M5] [Corpus: product §F6] [Corpus: product §F7]  
> [Corpus: tests] [Corpus: tech-spec] [Corpus: decisions] [Corpus: adr/ADR-007]

```text
QA Results:
  Lint:           PASS — 0 issues (ruff + eslint)
  Format:         PASS — 0 files (ruff format + prettier)
  Typecheck:      PASS — 0 errors (pre-existing basedpyright warnings)
  Tests (Python): PASS — tip CI full matrix; local test-unit-fast 794+; H0c 6/6
  Tests (FE):     PASS — tip CI Test (frontend); local Help Vitest 107/107
  Coverage:       PASS — package + per-file ≥95% Python (auth+worker incl.); FE lines ~94.7% out of D-S056-cov95-scope
  Security:       PASS — uvx pip-audit 0 CVEs; no pickle.loads; rg eval/exec only benign RegExp.exec
  Cross-file:     PASS — lint clean on scoped trees
  Dependencies:   N/A delta — no new runtime deps (06 skipped)
  Template:       PASS — apps/{backend,frontend,worker} + packages layout
  Data / Modal:   N/A — no Modal/data-staging this cycle
  Connectivity:   PASS (H0c); H4–H5 staging waived (12/13); local Help T2 via browser MCP
  Tip CI:         PASS — run 31286442836 @ 3ca4f438
```

## Overall: **pass_with_advisories**

### Blocking

| Check | Status | Evidence |
|-------|--------|----------|
| Lint / format | PASS | `make lint` / `make format-check` |
| Typecheck | PASS | `make typecheck` — 0 errors |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` 6/6 |
| Fast units + per-file cov | PASS | `make test-unit-fast` + checker |
| Tip CI | PASS | [31286442836](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31286442836) |
| Converter perf CI | PASS | job green on tip |
| Security (pip-audit) | PASS | 0 known vulns |

### Advisories (QA-IDs for 11-verify-impl)

| ID | Finding | Severity | Suggested action |
|----|---------|----------|------------------|
| QA-001 | T1.5 GH ruleset apply blocked — token lacks admin (`D-S056-t15-admin`) | advisory | Admin run `scripts/deploy/apply_gh_branch_rulesets.sh` later; script already lists `Converter perf (tac2iwxxm)` |
| QA-002 | Local `tests/integration -m "not live"` 4/4 skipped (DB/env); tip CI covered matrix | advisory | Accept for this cycle |
| QA-003 | `scripts/check_secrets.sh` / gitleaks not installed locally | advisory | Rely on CI + pip-audit |
| QA-004 | H4–H5 / 12/13 deploy smoke waived by routing | advisory | Confirm at 11; merge gate = tip CI → `stage` |
| QA-005 | Frontend Vitest lines/statements ~94.7% (below 95) | advisory | Out of `D-S056-cov95-scope=2` (Python-only); optional follow-up |
| QA-006 | Local Playwright CLI hung (Chromium launch); UJ-054 verified via Vitest T0 + browser MCP | advisory | Accept MCP T2 evidence; CI E2E Smoke green |

### AC → evidence map

| AC | TC | Status |
|----|-----|--------|
| AC1–AC4 husky | TC-EV047-001..004 | met (M2 commits + tip CI offloads remain) |
| AC5–AC6 perf | TC-EV047-005..008 | met in CI (job green); **ruleset ops half** = QA-001 |
| AC7 one-pager | TC-EV047-009 | met — `docs/guides/operator-one-pager.md` |
| AC8 handbook | TC-EV047-010 | met — `docs/guides/operator-handbook.md` |
| AC9 Help/README | TC-EV047-011 / UJ-054 | met — README links + `data-testid=operator-help-link` |
| Cov95 | D-S056-cov95-scope=2 | met — Python package + per-file ≥95 incl. auth/worker |

### Commands run (reproducible)

```bash
make format-check
make lint
make typecheck
make test-unit-fast
uv run pytest tests/unit/test_cors_policy.py -q --tb=line
uv run pytest tests/integration -q --tb=line -m "not live"
pnpm --filter @metar/frontend exec vitest run \
  src/utils/operatorHelp.test.ts src/app/components/FileConverter.test.tsx
uvx pip-audit
# Tip CI: gh run view 31286442836
```

### Next

1. **10-e2e** report (parallel) — UJ-054  
2. **11-verify-impl** — AC sign-off + advisory disposition  
3. Merge still requires user approval on #961 (do not auto-merge)
