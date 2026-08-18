# QA report — 09-qa (S070 / EV-060)

> Generated: 2026-08-18  
> Scope: delta (`D-S070-09-depth=2a`) — EV-060 surfaces + blocking H0c  
> Branch: `evolve/EV-060-converter-operator-bugs`  
> Tip: `6a87c96a` (reports/tests this stage uncommitted at run time)  
> Corpus: [Corpus: tests] [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F2] [Corpus: product §F29] [Corpus: product §F31] [Corpus: decisions §EV-060]

```text
QA Results:
  Lint:           PASS — 0 issues (make lint)
  Format:         PASS — 0 files after Prettier on new e2e spec
  Typecheck:      PASS — 0 errors (pre-existing basedpyright warnings in auth/tac2iwxxm)
  Tests (Python): PASS — H0c 6/6; EV-060 backend 25 passed; tac-validate AHL 9 passed
  Tests (FE):     PASS — 9 passed (tc-ev060-1002 + tc-ev060-1005 Vitest)
  Security:       PASS — gitleaks tree PASS; pip-audit SKIPPED (advisory)
  Cross-file:     PASS — no pickle.loads / eval( / exec( in app logic (RegExp.exec only)
  Dependencies:   SKIPPED — pip-audit not in default delta env
  Template:       PASS — static+api+worker; no new deployables
  Data / Modal:   N/A — no Modal in EV-060
```

**Overall: PASS** (delta) with advisories below.

## Executive summary

| Check | Status | Blocking? | Notes |
|-------|--------|-----------|-------|
| Format | PASS | no | `make format-check` after Prettier on `apps/e2e/tc-ev060-uj059-063.e2e.spec.ts` |
| Lint | PASS | no | `make lint` (ruff + eslint `--max-warnings 0`) |
| Typecheck | PASS | no | `make typecheck` — 0 errors |
| Secrets | PASS | **yes if fail** | `make secrets-check` / gitleaks |
| YAML / Actions | PASS | no | actionlint + yamllint |
| H0c CORS | PASS | **yes** | `tests/unit/test_cors_policy.py` 6/6 |
| H0i integration | SKIPPED | advisory | full `tests/integration` not in delta 09 |
| H4–H5 staging | deferred | advisory | 12/13 |
| pip-audit | SKIPPED | advisory | delta 09 |
| Full backend coverage suite | not re-run | no | 08 M4: 1369 passed, 98.17% |

## Commands run

```bash
make format-check
make lint
make typecheck
make secrets-check
make validate-yaml
uv run pytest tests/unit/test_cors_policy.py -q
cd apps/backend && uv run pytest \
  tests/unit/test_tc_ev060_1001_lint_tac_ahl.py \
  tests/unit/test_tc_ev060_1003_iwxxm_product.py \
  tests/unit/test_tc_ev060_1004_log_level.py \
  tests/unit/test_tc_ev060_1005_bulletin_fields.py -q
uv run pytest packages/tac-validate/tests/test_tc_ev060_1001_ahl_heading.py -q
cd apps/frontend && pnpm exec vitest run \
  src/test/tc-ev060-1002-profile-picker.workflow.test.tsx \
  src/test/tc-ev060-1005-bulletin-fields.workflow.test.tsx
```

Subset pytest exits 1 on `--cov-fail-under=98` when run alone (24.95% of the whole backend tree). All **25 collected EV-060 tests passed**; coverage gate remains the full `make test-unit-backend` from 08.

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | advisory | Host `.env` may set `PLAYWRIGHT_BASE_URL=http://localhost:5173` (S047 residual). Playwright global-setup then waits on the wrong port. | Always pass `PLAYWRIGHT_BASE_URL=http://localhost:18000` and `PLAYWRIGHT_API_BASE_URL=http://localhost:18001` for local T2. |
| QA-002 | advisory | `make dev` rewrites `apps/frontend/public/config.json` (Prettier drift). | Restore before commit; do not commit the generated file. |
| QA-003 | advisory | H4–H5 live staging not run. | 12/13 after PR → `stage`. |
| QA-004 | advisory | pip-audit not run in this delta. | CI medium / user-requested remediation. |
| QA-005 | **see 10-e2e** | Local OpenAPI has `/auth/login` and `/auth/me` only — **no `POST /auth/logout`**. Scoped logout in FileConverter POSTs `/auth/logout` → **404**. | 11: reconcile UAT-003 ACCEPTED vs T2 FAIL; restore logout route or change FE. Not fixed in 09 (report-only). |

## Connectivity

- Blocking H0c: **PASS** (6/6)
- Artifacts present: `tests/smoke/test_staging_connectivity.py`, `scripts/deploy/verify_connectivity.sh`
- CORS: no new origins (`D-S070-e7`)
- H4–H5 / staging: **deferred** to 12/13

## Phase alignment

M1–M4 08 PASS. 09 is delta assessment only — no product fixes. Next: 10-e2e findings + **11-verify-impl**. Promote held. Do not merge without user OK.
