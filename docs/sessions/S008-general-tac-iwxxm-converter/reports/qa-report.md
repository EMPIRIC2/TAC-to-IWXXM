# QA Report — S008 / EV-006 Phase D

> **Generated**: 2026-07-12  
> **Skill**: 09-qa (delta)  
> **Session**: S008-general-tac-iwxxm-converter  
> **Cycle**: EV-006 (F6, F2, F8)  
> **Branch**: `evolve/S008-general-tac-iwxxm-converter`  
> **Mode**: delta — post C→D; full monorepo gates for affected Fn surface

```text
QA Results:
  Lint:           PASS — 0 issues
  Format:         PASS — 0 files
  Typecheck:      PASS — 0 errors (py + js)
  Tests (Python): PASS — make test-unit (backend 1120, packages, worker, bugs); H0c 6 pass
  Tests (FE):     PASS — frontend vitest coverage ≥98%
  Security:       PASS — secrets tree 0; gitleaks --no-git 0; no eval/exec/pickle.loads in apps/packages
  Cross-file:     PASS — ruff unused clean (lint)
  Dependencies:   ADVISORY — pip-audit lockfile audit env-limited (Py≥3.12); see QA-001
  Template:       PASS — apps/{backend,frontend,worker} + packages; render.yaml present; no modal in apps/packages
  Data / Modal:   ADVISORY — docs/data-staging-state.md absent (N/A for this template); Modal N/A
  Connectivity:   H0c PASS; H0i integration skipped (no live env); H4–H5 staging URLs unset → QA-002
```

**Overall: pass_with_advisories**

## Executive summary

| Check | Blocking? | Status | Notes |
|-------|-----------|--------|-------|
| Format (`make format-check`) | Yes | PASS | ruff + prettier |
| Lint (`make lint`) | Yes | PASS | py + js |
| Typecheck (`make typecheck`) | Yes | PASS | basedpyright + tsc |
| Unit tests (`make test-unit`) | Yes | PASS | cov gates met |
| Frontend unit | Yes | PASS | statements 98.65% |
| H0c CORS | Yes | PASS | 6 passed |
| H0i integration | Yes* | PASS | 7 skipped (env-gated); 0 failed |
| Secrets / gitleaks (tree) | Yes | PASS | no leaks |
| Dangerous patterns | Yes | PASS | none in app code |
| Template layout | Yes | PASS | `static+api+worker` |
| pip-audit | Advisory | SKIPPED/limited | QA-001 |
| H4–H5 live staging | Advisory | SKIPPED | QA-002 — no staging frontend URL in env |
| data-staging-state.md | Advisory | N/A | QA-003 |

\*H0i: missing live DB/env → skips OK per connectivity-gates.

## Commands run

```bash
make format-check
make lint
make typecheck
make test-unit
make test-unit-frontend
uv run pytest tests/unit/test_cors_policy.py tests/integration -q
gitleaks detect --no-git --config .gitleaks.toml
rg secrets / dangerous patterns over apps packages tests
```

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | advisory | Project `pip-audit -r` lockfile install fails on host Python 3.11 vs requires-python ≥3.12 | Run pip-audit inside `.venv` / CI job only; do not block |
| QA-002 | advisory | H4–H5 staging connectivity not re-run (no `METAR_STAGING_*` / Playwright live URL in this shell) | Optional: `make test-live-connectivity` when staging URLs available; 12/13 skipped this cycle |
| QA-003 | advisory | `docs/data-staging-state.md` not present | N/A for Render+vendor schemas; omit or add stub if corpus requires |
| QA-004 | advisory | Uncommitted 08 fix-in-place still on working tree during 09 | Commit before PR to main / 11 sign-off |

## Phase / plan alignment

- Execution plan: **51/51** tasks complete; Phase C closed; C→D **passed** (`D-S008-EV006-c-to-d`).
- Routing: `09-qa` + `10-e2e` parallel → then `11-verify-impl`.
- Deploy stages 12/13: **skipped** in S008 routing (build+verify cycle).

## Notes

- 09 is **report-only** — no auto-fixes applied in this stage.
- Playwright local smoke is owned by **10-e2e** (see `e2e-report.md`).
