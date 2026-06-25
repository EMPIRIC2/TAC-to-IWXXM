# QA Report — S006 / EV-005 (09-qa)

> Generated: 2026-06-25  
> Scope: Delta QA for GitHub [#664](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/664) — custom output filename for manual METAR input  
> Branch: `feat/S006-issue-664-output-filename`  
> Session: S006-issue-664-output-filename | Evolve cycle: EV-005 | Features: F1 (extended), F5 (conversion_params persist)  
> Build status: **complete** — `07-build` and `08-verify-build` PASS on routing plan

```text
QA Results (S006 delta + blocking connectivity):
  Lint (Python):  PASS — 0 issues
  Lint (JS):      PASS — 0 issues
  Format:         PASS — 413 files
  Typecheck:      PASS — 0 errors (basedpyright + tsc)
  Tests (Python): PASS — workspace 43, backend 1154, auth 228 (31 skip), gifts 1010 (1 skip), bugs 37
  Tests (H0c):    PASS — 6/6 (tests/unit/test_cors_policy.py)
  Tests (H0i):    PASS — 8/8 (apps/backend/tests/integration/test_h0i_connectivity.py)
  Tests (FE):     PASS — 530 passed (Vitest, via make test-unit)
  Security:       PASS — 0 CVEs (lockfile); 0 tree leaks (gitleaks)
  Cross-file:     0 F401/F841; 0 cycles; 358 docstring gaps (advisory)
  Dependencies:   20 outdated (advisory); 0 missing
  Template:       PASS — static+api monorepo layout
  Config guard:   PASS — 8/8 (placeholders + H5 runtime config)
  env-check:      PASS with advisory (legacy SUPABASE_SERVICE_ROLE_KEY name)
  npm audit:      PASS — 0 vulnerabilities
  Connectivity:   H0c/H0i PASS; H4–H5 SKIPPED (no LIVE_* / staging URLs set)
  Live stack:     7 skipped (tests/integration — RUN_LIVE_TESTS unset)
```

**Overall: PASS** — all blocking checks green. Advisories deferred to **11-verify-impl**.

---

## Executive summary

| Category | Status | Blocking |
|----------|--------|----------|
| Lint / format / typecheck (Python + JS) | PASS | — |
| Unit tests (Python + frontend) | PASS | — |
| H0c CORS policy | PASS | Yes — green |
| H0i in-process connectivity | PASS | Yes — green |
| pip-audit (lockfile export) | PASS | — |
| gitleaks (pre-commit) | PASS | — |
| Config guard + env-check | PASS | — |
| npm audit (frontend) | PASS | — |
| EV-005 feature scope (F1/F5) | PASS | — |
| H4–H5 live connectivity | SKIPPED | QA-001 |
| Live stack integration | SKIPPED | QA-002 |
| Public docstrings missing | Advisory | QA-003 |
| Outdated PyPI packages | Advisory | QA-004 |
| GIFTs tpg eval/exec | Advisory | QA-005 |
| Legacy env var name warning | Advisory | QA-006 |

---

## EV-005 feature coverage (#664)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| R1 — Frontend-only | PASS | Changes in `apps/frontend/src/utils/outputFilename.ts`, `FileConverter.tsx` |
| R2 — Blank ⇒ `manual_input` | PASS | `outputFilename.test.ts` |
| R3 — Manual only; uploads unchanged | PASS | `FileConverter.test.tsx` describe block `#664 / EV-005` |
| R4 — Multi-line `_1/_2` suffix | PASS | `manualOutputName()` unit tests |
| R5 — Persist across reload | PASS | `conversion_params.output_filename` restore test |
| R6 — Carry via conversion_params JSONB | PASS | No API/migration change; guest state tests |
| R7 — ZIP archive renamed to custom base | PASS | `outputArchiveName()` tests |
| E2E journey | Present | `apps/e2e/tac-file-conversion.e2e.spec.ts` — custom filename test |

No backend contract changes; blocking Python suites unchanged and green.

---

## Commands run

```bash
# Lint / format / typecheck
uv run ruff check apps/backend/src apps/backend/tests packages/auth/src packages/auth/tests \
  packages/gifts/gifts packages/gifts/tests packages/shared packages/shared/tests tests
uv run ruff format --check apps packages tests
make typecheck
pnpm run lint:js

# Connectivity (blocking)
uv run pytest tests/unit/test_cors_policy.py -v
cd apps/backend && uv run pytest tests/integration/test_h0i_connectivity.py -v --no-cov

# Tests
make test-unit

# Security
make secrets-check
uv export --frozen --no-dev -o /tmp/pip-audit-req.txt && uv run pip-audit -r /tmp/pip-audit-req.txt
uv run ruff check --select F401,F841 apps packages tests

# Config / audit
make config-guard env-check audit-frontend

# Integration (live — env-gated)
uv run pytest tests/integration -v
```

---

## Per-check details

### Lint (Python) — PASS

`ruff check` on all `PY_LINT` paths: **0 issues**.

### Lint (JS) — PASS

`pnpm run lint:js` (ESLint on frontend, e2e, shared): **0 errors, 0 warnings**.

### Format — PASS

`ruff format --check apps packages tests`: **413 files already formatted**.

### Typecheck — PASS

- `basedpyright` on `packages/shared`, `packages/auth`, `apps/backend`: **0 errors**
- `pnpm run typecheck:js` (frontend, shared, e2e tsc): **0 errors**

### Tests (Python) — PASS

| Package | Result |
|---------|--------|
| Workspace (`tests/unit` + migration smoke) | 43 passed |
| `apps/backend` | 1154 passed (98.04% cov) |
| `packages/auth` | 228 passed, 31 skipped |
| `packages/gifts` | 1010 passed, 1 skipped |
| `tests/bugs` | 37 passed, 1 deselected |

### Tests (Frontend) — PASS

`make test-unit-frontend`: **530 passed** (98.95% stmt cov per 08-verify-build).

### H0c / H0i — PASS

- `tests/unit/test_cors_policy.py`: **6/6**
- `apps/backend/tests/integration/test_h0i_connectivity.py`: **8/8**

### Security — PASS

| Layer | Result |
|-------|--------|
| gitleaks (pre-commit `--all-files`) | Passed |
| pip-audit (uv lockfile export) | No known vulnerabilities |
| Dangerous patterns (`eval`/`exec`/`pickle.loads` in apps/) | None |
| GIFTs `tpg.py` | `eval`/`exec` in third-party parser generator — advisory only (QA-005) |

### Cross-file — PASS (advisories)

- F401/F841: **0**
- Circular import cycles: **none detected** (workspace layout)
- Public symbols without docstrings in `apps/` + `packages/`: **358** (advisory QA-003)

### Dependencies — PASS (advisory)

`uv pip list --outdated`: **20 packages** with newer versions available (anyio, fastapi, ruff, etc.). Pins intentional per `docs/dependency-inventory.md` — advisory QA-004.

### Template conformance — PASS

| Criterion | Status |
|-----------|--------|
| Layout `apps/*`, `packages/*`, `tests/`, `vendor/schemas` | OK |
| Template `static+api` | OK — no Modal worker paths |
| CI workflow `.github/workflows/ci-cd.yml` | Present; `make validate-ci` gates match Makefile |
| Connectivity scripts | `scripts/deploy/verify_connectivity.sh`, `tests/smoke/test_staging_connectivity.py` present |

### Config / env — PASS (advisory)

- `make config-guard`: **8/8** passed
- `scripts/env/verify-sync.sh`: PASS — warns `SUPABASE_SERVICE_ROLE_KEY` without canonical `SUPABASE_SECRET_KEY` (QA-006)

---

## Connectivity (stage 09)

| Tier | Status | Notes |
|------|--------|-------|
| H0c | **PASS** | Blocking — 6/6 unit tests |
| H0i | **PASS** | Blocking — 8/8 in-process integration |
| H3–H6 live | SKIPPED | `RUN_LIVE_TESTS` / `METAR_STAGING_*` unset |
| H4–H5 | SKIPPED | QA-001 — run `scripts/deploy/verify_connectivity.sh` at deploy |

---

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | Advisory | H4–H5 live connectivity not exercised (no staging URLs in env) | Defer to **12-verify-deploy** / **13-deploy-smoke** per routing plan |
| QA-002 | Advisory | `tests/integration/test_live_stack.py` — 7 tests skipped (`RUN_LIVE_TESTS` unset) | Expected for local QA; run before production sign-off |
| QA-003 | Advisory | 358 public Python symbols lack docstrings | Optional doc pass; not blocking |
| QA-004 | Advisory | 20 outdated PyPI packages | Bump via intentional ADR cycle if desired |
| QA-005 | Advisory | `packages/gifts/gifts/common/tpg.py` uses `eval`/`exec` (upstream parser) | Known; no action unless upgrading GIFTs fork |
| QA-006 | Advisory | `env-check` warns legacy `SUPABASE_SERVICE_ROLE_KEY` | Migrate to `SUPABASE_SECRET_KEY` (S003 follow-on) |

No blocking findings.

---

## Phase / execution-plan alignment

- **Session S006** routing: `07-build` ✅, `08-verify-build` ✅, `09-qa` ✅ (this report)
- **Next:** `10-e2e` (Playwright `#664` custom filename journey), then `11-verify-impl`
- **Deferred:** `12-verify-deploy` / `13-deploy-smoke` optional per routing plan (frontend static deploy only if user requests)

---

## Handoff

Proceed to **10-e2e** and **11-verify-impl**. No code fixes required from 09-qa. User may approve advisories QA-001–QA-006 as defer or fix-now during verify-impl.
