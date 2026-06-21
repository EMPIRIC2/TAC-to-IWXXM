# QA Report — Stage 09

> Generated: 2026-06-20  
> Scope: Full codebase (`static+api` monorepo migration)  
> Branch: `main`  
> Execution plan: Phase 4 / M11 complete (pending Phase 4 gate PR)

```text
QA Results:
  Lint:           PASS — 0 issues (5 invalid noqa warnings advisory)
  Format:         PASS — 0 files need reformat (371 checked)
  Typecheck:      PASS — 0 errors (shared, auth, backend)
  Tests (Python): PASS_WITH_NOTE — unit/coverage green; TC-M001 flaky in full migration collection
  Tests (FE):     PASS — frontend 96.95% lines; shared JS 84.61% lines
  Security:       FAIL — 1 HIGH CVE (msgpack 1.2.0); 0 secrets (tree); 0 history
  Cross-file:     PASS — 0 unused imports; 0 cycles detected; docstrings not scanned
  Dependencies:   14 outdated (advisory); msgpack fix available (1.2.1)
  Template:       PASS — monorepo layout; .gitmodules absent
  Connectivity:   H0c PASS (6/6); H0i PASS (7/7); H4 SKIPPED; integration matrix NOT RUN
```

**Overall: FAIL** — blocking: `msgpack` HIGH CVE (GHSA-6v7p-g79w-8964)

---

## Executive summary

| Category | Status | Blocking |
|----------|--------|----------|
| Lint / format / typecheck | PASS | — |
| Python unit + coverage (95% gate) | PASS | — |
| Frontend unit + coverage | PASS | — |
| Migration gates TC-M003–M005 | PASS | — |
| TC-M001 (`make test-unit` smoke) | FLAKY | Advisory (QA-001) |
| H0c CORS policy | PASS | — |
| H0i connectivity logic | PASS | — |
| pip-audit | FAIL | **Yes** |
| gitleaks (tree + history) | PASS | — |
| Live staging H4 | SKIPPED | Advisory (QA-006) |
| Docker integration matrix | NOT RUN | Advisory (QA-006) |
| Legacy path cleanup | PARTIAL | Advisory (QA-002) |
| badge_audit script | FAIL | Advisory (QA-002) |

Improvement since **08-verify-build** (2026-06-20): typecheck, format, and lint are now green. The prior FAIL on basedpyright (1131+ errors) is resolved. New blocking finding: transitive **msgpack 1.2.0** HIGH CVE.

---

## Commands run

Environment: Linux, Node v22.23.0, Python 3.12.12 (uv venv), branch `main`.

```bash
# Phase 1 — sync
uv sync

# Quality gates (CI parity — .github/workflows/ci-cd.yml quality-gates job)
uv run ruff check apps/backend/src apps/backend/tests \
  packages/auth/src packages/auth/tests \
  packages/gifts/gifts packages/gifts/tests \
  packages/shared packages/shared/tests tests

uv run ruff format --check apps packages tests

uv run basedpyright packages/shared/src
cd packages/auth && uv run basedpyright
cd ../../apps/backend && uv run basedpyright

pnpm install --frozen-lockfile
pnpm run lint:js
pnpm run format:check
pnpm run typecheck:js

# Unit tests + coverage (per CI jobs)
uv run pytest packages/shared/tests --cov=metar_shared --cov-fail-under=95 -q
cd apps/backend && uv run pytest tests/unit --cov=src --cov-fail-under=95 -q
cd packages/auth && uv run pytest tests --cov=src --cov-fail-under=95 -q
cd packages/gifts && uv run pytest tests/ --cov=gifts --cov=validation --cov-fail-under=95 -q

pnpm --filter @metar/frontend run test:coverage
pnpm --filter @metar/shared run test:coverage

# Migration + connectivity
uv run pytest tests/unit/test_cors_policy.py -v
cd apps/backend && uv run pytest tests/integration/test_h0i_connectivity.py -v
uv run pytest tests/migration/test_tc_m003_golden_conversion.py \
  tests/migration/test_tc_m004_no_submodule_refs.py \
  tests/migration/test_tc_m005_auth_merge.py -v
uv run pytest tests/migration -q                    # full collection — TC-M001 failed
uv run pytest tests/migration/test_tc_m001_monorepo_clone_smoke.py -v  # isolated — PASS

# Security
uv pip install pip-audit && uv run pip-audit
gitleaks detect --no-git --config .gitleaks.toml
gitleaks detect --config .gitleaks.toml
rg -l "BEGIN (RSA |OPENSSH )?PRIVATE KEY|sk_live_|AKIA" apps/ packages/ tests/ scripts/

# Config guard
uv run pytest tests/test_config_placeholders.py -v

# Staging (env-gated)
uv run pytest tests/smoke/test_staging_connectivity.py -v

# Template / misc
python3 .github/scripts/badge_audit.py
uv pip list --outdated
```

**Not run locally** (requires Supabase env + docker-compose):

```bash
make test-integration   # H0i live stack — CI integration-matrix job
```

---

## Per-check details

### Lint — PASS

```
All checks passed!
```

Advisory: 5 invalid `# noqa` directives in `packages/gifts/gifts/{METAR,SWA,TAF,TCA,VAA}.py` (upstream GIFTs style).

### Format — PASS

```
371 files already formatted
```

### Typecheck — PASS

```
packages/shared/src: 0 errors, 0 warnings, 0 notes
packages/auth:         0 errors, 0 warnings, 0 notes
apps/backend:          0 errors, 0 warnings, 0 notes
```

### Tests (Python) — PASS with advisory

| Suite | Result |
|-------|--------|
| `packages/shared` | 26 passed, 95.47% cov |
| `apps/backend` unit | 969 passed, 95.17% cov |
| `packages/auth` | 187 passed, 31 skipped, 96.37% cov |
| `packages/gifts` | 978 passed, 1 skipped, 95.41% cov |
| `tests/unit` + migration (subset) | 152 passed, 1 skipped |
| `tests/test_config_placeholders` | 2 passed |
| `tests/migration` (full) | **121 passed, 1 failed** |
| TC-M001 isolated | 8 passed, 1 skipped |

**TC-M001 failure (full migration collection):**

```
FAILED tests/migration/test_tc_m001_monorepo_clone_smoke.py::TestTcM001MonorepoCloneSmoke::test_make_test_unit_succeeds
======= 1 failed, 121 passed, 1 skipped in 270.46s =======
```

Same test **passes** when the TC-M001 module runs alone (~278 s, dominated by `make test-unit`). Likely subprocess/resource interference when collected with the full migration suite (see QA-001).

### Tests (Frontend) — PASS

| App | Statements | Lines | Gate |
|-----|------------|-------|------|
| `@metar/frontend` | 96.43% | 96.95% | ≥95% implied by Codecov |
| `@metar/shared` (JS) | 84.61% | 84.61% | No vitest threshold configured (QA-003) |

ESLint, Prettier, and `tsc --noEmit` all pass.

### Security — FAIL (blocking)

**pip-audit:**

```
Found 1 known vulnerability in 1 package
Name    Version ID                  Fix Versions
msgpack 1.2.0   GHSA-6v7p-g79w-8964 1.2.1
```

Severity: **HIGH** (CVSS 7.5 — out-of-bounds read / crash on Unpacker reuse). Transitive via `locust` → `msgpack` in `uv.lock`.

Workspace packages correctly skipped (not on PyPI): gifts, metar-auth, metar-backend, metar-shared.

**Secrets scan:**

- gitleaks working tree (~1.25 GB): **no leaks**
- gitleaks git history (230 commits): **no leaks**
- ripgrep pattern scan: one hit in `tests/test_auth_frontend_integration.py` — fixture string `sk_live_abcd1234...` (test data, not a live credential)

**Dangerous patterns (advisory):**

- `eval()` / `exec()` in `packages/gifts/gifts/common/tpg.py` (upstream GIFTs parser generator — unchanged per REQ-016)

### Cross-file — PASS (partial scan)

| Check | Result |
|-------|--------|
| F401/F841 unused imports | 0 |
| Circular deps | Not automated; no import cycles observed in spot checks |
| Public docstrings | SKIPPED (advisory backlog from 08-verify-build) |
| vulture dead code | SKIPPED |

### Dependencies — Advisory

14 outdated packages (`uv pip list --outdated`), including msgpack 1.2.0 → 1.2.1. Pins are intentional per ADR-005; only msgpack CVE is blocking.

### Template conformance — PASS

| Criterion | Status |
|-----------|--------|
| `apps/backend`, `apps/frontend`, `apps/e2e` | Present |
| `packages/auth`, `packages/gifts`, `packages/shared` | Present |
| `vendor/schemas/*` + `vendor/manifest.json` | Present, pinned |
| `.gitmodules` | Absent ✓ |
| Separate auth deployable | None ✓ |
| `import modal` outside infra | N/A (no Modal in this template) |

**Legacy remnants (post-M11 partial):** `backend/`, `auth/`, `schemas/` directories still exist; `frontend/` and `GIFTs/` removed. See QA-002.

### Connectivity

| Gate | Result | Notes |
|------|--------|-------|
| **H0c** | **PASS** (6/6) | `tests/unit/test_cors_policy.py` |
| **H0i** | **PASS** (7/7) | `apps/backend/tests/integration/test_h0i_connectivity.py` — tests pass; isolated run exits 1 only due to default `--cov` 95% gate on partial tree |
| **H4** | SKIPPED | `STAGING_API_URL` / `STAGING_FRONTEND_ORIGIN` unset |
| **Integration matrix** | NOT RUN | Requires Supabase secrets + `docker compose` (CI job `integration-matrix`) |

Phase 4 notes in execution plan: T11.4 H4/H5 green on staging per workflow-state — local re-verify deferred without env.

### Data / vendor

| Asset | Status |
|-------|--------|
| Vendor snapshots (iwxxm, codelists, modelling, translation) | Present under `vendor/schemas/`; manifest pins verified |
| Golden METAR fixtures | Present (`apps/backend/test-data`, TC-M003 pass) |
| D6/D7 Modal assets | N/A (`static+api` template — no Modal) |

---

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-001 | Advisory | TC-M001 `test_make_test_unit_succeeds` fails in full `tests/migration` collection but passes in isolation | Investigate pytest collection order / subprocess contention; consider marking test `@pytest.mark.last` or splitting heavy `make test-unit` into CI-only gate |
| QA-002 | Advisory | Legacy dirs `backend/`, `auth/`, `schemas/` remain; `badge_audit.py` still references removed `frontend/`, `GIFTs/`, submodule paths | Complete T11.1 cleanup; update badge audit paths to monorepo layout |
| QA-003 | Advisory | `@metar/shared` JS coverage 84.61% — no vitest threshold; Python shared at 95% | Align JS coverage gate with ADR-007 or document exception |
| QA-004 | **Blocking** | `msgpack` 1.2.0 HIGH CVE (GHSA-6v7p-g79w-8964) via locust | Bump to 1.2.1 in lockfile (`uv lock --upgrade-package msgpack`) |
| QA-005 | Advisory | Invalid `# noqa` directives in upstream GIFTs encoder modules | Fix or suppress in packages/gifts ruff config |
| QA-006 | Advisory | H4 live staging + docker integration matrix not re-run locally | Re-run with staging URLs per `docs/deploy.md` runbook before Phase 4 gate PR merge |
| QA-007 | Advisory | `datetime.utcnow()` deprecation warnings in backend/gifts during TC-M005 | Migrate to timezone-aware UTC (non-blocking) |

---

## Phase / execution-plan alignment

- **Active phase:** Phase 4 — CI, Deploy & Validate  
- **M11:** All tasks marked complete in execution plan  
- **07-build:** `in_progress` in workflow-state (task loop notes Phase 4 gate met on main) — recommend marking complete after this QA cycle  
- **08-verify-build:** Was FAIL (typecheck); superseded by this run — typecheck now PASS  
- **Deferred gates:** Live H4/H5 re-verify locally (QA-006); Phase 4 major PR (PR-9) pending user approval  

---

## Handoff notes

1. **Fix QA-004 first** — msgpack bump is the sole blocking FAIL for 09 PASS.  
2. Walk **QA-001** with user — flaky migration gate may affect CI if `tests/migration` runs in full on every push.  
3. **Do not re-run full 09** until msgpack is resolved unless codebase changes materially.  
4. Typecheck remediation from 08-verify-build appears complete — no basedpyright errors remain.
