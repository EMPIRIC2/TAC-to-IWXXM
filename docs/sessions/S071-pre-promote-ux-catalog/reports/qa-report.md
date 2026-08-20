# QA report — 09-qa (S071 / EV-061)

> Generated: 2026-08-20  
> Scope: delta — EV-061 surfaces (#1010–#1015) + blocking H0c/H0i  
> Branch: `evolve/EV-061-pre-promote-ux-catalog`  
> Tip: `b6ce485d` (+ local 09/10 commits)  
> Corpus: [Corpus: tests] [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F6]
> [Corpus: product §F9] [Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34]
> [Corpus: decisions §EV-061] [Corpus: deploy]

```text
QA Results:
  Lint:           PASS — 0 issues (make lint)
  Format:         PASS — 0 files (make format-check)
  Typecheck:      PASS — 0 errors (make typecheck; pre-existing basedpyright warnings in tac2iwxxm)
  Tests (Python): PASS — H0c 6/6; H0i 10/10; EV-061 backend/tac2iwxxm 12; promote-gate 9; bulletin 1
  Tests (FE):     PASS — 16 passed (tc-ev061-1010..1014 Vitest)
  Security:       PASS — gitleaks tree PASS; actionlint + yamllint PASS
  Cross-file:     PASS — CI jobs Lint/Typecheck/E2E Full present (TC-EV061-1015)
  Dependencies:   SKIPPED — pip-audit not in default delta env
  Template:       PASS — static+api+worker; no new deployables
  Data / Modal:   N/A — no Modal in EV-061
```

**Overall: PASS** (delta) with advisories below.

## Executive summary

| Check | Status | Blocking? | Notes |
|-------|--------|-----------|-------|
| Format | PASS | no | `make format-check` |
| Lint | PASS | no | `make lint` |
| Typecheck | PASS | no | `make typecheck` — 0 errors |
| Secrets | PASS | **yes if fail** | `make secrets-check` / gitleaks |
| YAML / Actions | PASS | no | actionlint + yamllint |
| H0c CORS | PASS | **yes** | `tests/unit/test_cors_policy.py` 6/6 |
| H0i integration | PASS | advisory→run | `apps/backend/tests/integration/test_h0i_connectivity.py` 10/10 |
| H4–H5 staging | deferred | advisory | 12/13 |
| pip-audit | SKIPPED | advisory | delta 09 |
| Promote gate contracts | PASS | no | TC-EV061-1015-001..002 |

## Commands run

```bash
make format-check && make lint && make typecheck
make secrets-check && make validate-yaml
uv run pytest tests/unit/test_cors_policy.py \
  tests/test_tc_ev061_1015_promote_gate.py \
  tests/unit/test_tc_ev061_1011_live_bulletin_files.py -q --no-cov
uv run pytest apps/backend/tests/unit/test_tc_ev061_1010_validate_decode.py \
  apps/backend/tests/unit/test_tc_ev061_1012_ahl_decode_convert.py \
  apps/backend/tests/unit/test_tc_ev061_1014_lint_issue_catalog.py \
  packages/tac2iwxxm/tests/test_tc_ev061_1012_ahl_decode.py -q --no-cov
cd apps/backend && uv run pytest tests/integration/test_h0i_connectivity.py -q --no-cov
cd apps/frontend && pnpm exec vitest run src/test/tc-ev061-*.tsx
```

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | advisory | Host `.env` may set `PLAYWRIGHT_BASE_URL` to `:5173` | Always override `:18000`/`:18001` for local T2 |
| QA-002 | advisory | H4–H5 live staging not run | 12/13 after PR → `stage` |
| QA-003 | advisory | Live GitHub rulesets empty (length=0) | Admin: `bash scripts/deploy/apply_gh_branch_rulesets.sh` before promote |
| QA-004 | advisory | pip-audit not run in this delta | CI medium / user-requested remediation |
| QA-005 | advisory | E2E Full skips on PRs to `stage` (by design) | Required only on `stage`→`main` |

## Connectivity

- Blocking H0c: **PASS** (6/6)
- H0i: **PASS** (10/10)
- Artifacts present: `tests/smoke/test_staging_connectivity.py`, `scripts/deploy/verify_connectivity.sh`
- CORS: no new origins
- H4–H5 / staging: **deferred** to 12/13

## Phase alignment

09-qa complete for EV-061 Build band. Parallel 10-e2e: see `reports/e2e-report.md`.
