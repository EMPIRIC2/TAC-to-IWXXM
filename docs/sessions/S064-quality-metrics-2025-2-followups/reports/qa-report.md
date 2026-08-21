# 09-qa — S064 / EV-055

**Date:** 2026-08-11  
**Verdict:** **PASS** (advisories below)  
**Tip:** `af7b61dc` · branch `evolve/EV-055-quality-metrics-2025-2-followups` (pushed; no open PR → `stage` yet)  
**Corpus:** [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13] [Corpus: journeys §UJ-056] [Corpus: tests] [Corpus: adr/ADR-035]

```text
QA Results:
  Lint:           PASS — ruff + eslint via validate-fast / lint-fast (clean tree)
  Format:         PASS — 0 files (make format-check)
  Typecheck:      PASS — 0 errors (make validate-fast)
  Tests (Python): PASS — backend 1339; iwxxm-validate 100 (+1 skip); H0c 6/6
  Tests (FE):     PASS — 1035 passed | 4 skipped; branches 95.03%
  Security:       PASS — gitleaks tree PASS; pip-audit 0 known
  Cross-file:     PASS — regex .exec only (no pickle/eval/exec app abuse)
  Dependencies:   PASS — pip-audit clean
  Template:       PASS — apps/* + packages/* + vendor/schemas
  Data / Modal:   N/A for this delta (no Modal deploy in EV-055)
  Integration:    PASS — compose H0i 16 + smoke 6 + backend integration 23 (retry after docker race)
```

## Checks

| ID | Check | Result |
|----|-------|--------|
| QA-001 | Lint / format (`make lint-fast` / `format-check`) | PASS (clean tree; transient prettier fail only while Playwright dirtied `config.json`) |
| QA-002 | Typecheck + validate-fast | PASS |
| QA-003 | Backend unit `make test-unit-backend` | PASS — 1339; coverage 98.23%; per-file ≥95% |
| QA-004 | Frontend unit `make test-unit-frontend` | PASS — 1035; stmts 98.88 / branches **95.03** / lines 99.36 (re-run solo after parallel coverage clash) |
| QA-005 | iwxxm-validate `make test-unit-iwxxm-validate` | PASS — 100 passed, 1 skipped; `c14n.py` 100% |
| QA-006 | H0c CORS `tests/unit/test_cors_policy.py` | PASS (6) |
| QA-007 | H0i / integration `make test-integration` | PASS — retry after first docker race; 23 + 16 + 6 |
| QA-008 | Secrets `make secrets-check` / gitleaks | PASS |
| QA-009 | pip-audit (`uv export --frozen --no-dev` + `uvx pip-audit --no-deps`) | PASS (0 known) |
| QA-010 | Template layout | PASS |
| QA-011 | Connectivity artifacts | PASS present |
| QA-012 | Tip CI @ `af7b61dc` | **PENDING** — no open PR → stage |
| QA-013 | H4–H5 live staging | SKIPPED → 12/13 |

## AC map (delta — EV-055 / F7.q + F2/F13)

| AC | Status | Evidence |
|----|--------|----------|
| AC1 | PASS | C14N panes + raw override — TC-EV055-001; Vitest QualityMetricsDetail |
| AC2 | PASS | match_status under C14N — TC-EV055-002; generator + corpus_metrics |
| AC3 | PASS | Python/FE C14N helpers — TC-EV055-003; `c14n.py` 100% |
| AC4 | PASS | 2025-2 Schematron enable (#980) — TC-EV055-004 |
| AC5 | PASS | SCHEMA_IMPORT_WARNING fix (#979) — TC-EV055-005 |
| AC6 | PASS (local) | Validate disposition chips + UJ-056 deepen — TC-EV055-007; see `e2e-report.md` |
| AC7 | PASS | Regenerated corpus_metrics + loader smoke — TC-EV055-006 |

## Advisories

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-ADV-001 | advisory | Tip CI not watched — no open PR for evolve branch → `stage` | Open PR in 12-verify-deploy; watch `ci.yml` |
| QA-ADV-002 | advisory | First `make test-integration` hit docker container race; retry PASS | Rely on CI Integration Matrix + this retry |
| QA-ADV-003 | advisory | Parallel Vitest+other jobs clashed on `coverage/.tmp`; solo re-run PASS | Avoid concurrent frontend coverage runs locally |
| QA-ADV-004 | advisory | Live H4–H5 staging smoke not run in 09 | Stages 12/13 after merge to stage |
| QA-ADV-005 | advisory | basedpyright warnings in `packages/auth` / `tac2iwxxm` (pre-existing) | Out of EV-055 scope unless 11 expands |

## Commands (repro)

```bash
make format-check
make validate-fast
make test-unit-backend
make test-unit-frontend
make test-unit-iwxxm-validate
uv run pytest tests/unit/test_cors_policy.py -q
make test-integration
uv export --frozen --no-dev -o /tmp/req-audit.txt && uvx pip-audit -r /tmp/req-audit.txt --no-deps
```

## Exit

→ **10-e2e** (parallel) then **11-verify-impl**
