# QA Report — S001 / EV-001 (Convert & Convert&Send UI)

> Generated: 2026-06-22  
> Scope: Delta QA for GitHub [#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656) — Convert & Convert&Send buttons  
> Branch: `feat/S001-convert-send-buttons`  
> Session: S001-convert-send-buttons | Evolve cycle: EV-001 | Feature: F1

```text
QA Results (S001 delta + blocking connectivity):
  Lint:           PASS — 0 issues (make lint)
  Format:         PASS — 388 Python + Prettier clean
  Typecheck:      PASS — 0 errors (basedpyright + tsc)
  Tests (Python): PASS — 1009 passed, 1 skipped (make test-unit)
  Tests (H0c):    PASS — 6/6 (tests/unit/test_cors_policy.py)
  Tests (H0i):    PASS — 82/82 (integration pytest, in-process)
  Tests (FE):     PASS — 422 passed (vitest); S001 delta 76/76
  Security:       PASS — 0 CVEs; 0 tree leaks (gitleaks --no-git)
  Cross-file:     1 F841 advisory (backend script, outside lint scope)
  Dependencies:   PASS — pip-audit clean; workspace pkgs skipped (expected)
  Template:       PASS — static+api monorepo layout
  Connectivity:   H0c/H0i PASS; H4–H5 SKIPPED (no LIVE_* env this run)
  Config guard:   PASS — 2/2 placeholder tests
  Badge audit:    PASS
```

**Overall: pass_with_advisories** — all blocking checks green; advisories below for **11-verify-impl**.

---

## Executive summary

| Category | Status | Blocking |
|----------|--------|----------|
| Lint / format / typecheck | PASS | — |
| Unit tests (Python + frontend) | PASS | — |
| H0c CORS policy | PASS | Yes — green |
| H0i integration (in-process) | PASS | Yes — green |
| pip-audit | PASS | — |
| gitleaks (working tree) | PASS | — |
| Issue #656 acceptance | PASS | — |
| Uncommitted S001 work | Advisory | QA-010 |
| `make test-integration` local Makefile | Advisory | QA-011 |
| H4–H5 live connectivity | SKIPPED | QA-012 (advisory) |
| Pre-existing F841 in backend script | Advisory | QA-013 |
| Pre-existing eval/exec in GIFTs tpg | Advisory | QA-014 |

### Issue #656 acceptance (F1)

| Requirement | Status | Evidence |
|-------------|--------|----------|
| **Convert** button (conversion only) | Implemented | `FileConverter.tsx` — aria-label `Convert METAR files to IWXXM XML` |
| **Convert&Send** button (convert + send) | Implemented | `handleConvertAndSend`, shared `databaseUpload.ts` |
| Send success/failure feedback | Implemented | Toasts + inline send-failure status in `FileConverter.tsx` |
| Retain Upload to Database (R2) | Implemented | Dialog flow unchanged |
| Unit tests | PASS | `FileConverter.test.tsx`, `databaseUpload.test.ts` |
| E2E one-click path | Present | `tac-file-upload-database.e2e.spec.ts` — "converted and sent with one click" |

---

## Commands run

```bash
# Quality gates (CI parity)
make lint
make format-check
make typecheck

# Blocking connectivity
uv run pytest tests/unit/test_cors_policy.py -v
uv run pytest tests/test_backend_auth_integration.py \
  tests/test_backend_frontend_integration.py \
  tests/test_auth_frontend_integration.py \
  tests/test_gifts_backend_integration.py \
  tests/test_integration.py -v

# Full unit suite
make test-unit

# S001 delta frontend tests
pnpm --filter @metar/frontend exec vitest run \
  src/app/components/FileConverter.test.tsx \
  src/utils/databaseUpload.test.ts \
  src/test/conversion-parameters-mapping.workflow.test.tsx
pnpm --filter @metar/frontend exec vitest run

# Security
uv run pip-audit
gitleaks detect --no-git --config .gitleaks.toml

# Cross-file / config
uv run ruff check --select F401,F841 apps packages tests
uv run pytest tests/test_config_placeholders.py -v
python3 .github/scripts/badge_audit.py
```

**Not run (env-gated — advisory):**

```bash
LIVE_API_URL=... LIVE_FRONTEND_URL=... bash scripts/deploy/verify_connectivity.sh  # H4–H5
make test-integration  # docker compose + smoke subset (see QA-011)
```

---

## Per-check details

### Lint / format / typecheck

All green. Matches `.github/workflows/ci-cd.yml` quality-gates job paths.

### Tests

| Suite | Result | Notes |
|-------|--------|-------|
| `make test-unit` | 1009 passed, 1 skipped | gifts coverage 98.79% |
| H0c | 6 passed | Blocking — green |
| H0i (direct pytest) | 82 passed | Blocking — green; 45 deprecation warnings (pre-existing) |
| Frontend full | 422 passed | 34 files |
| S001 delta | 76 passed | 3 files |
| Config placeholders | 2 passed | CI config-guard parity |

### Security

- **pip-audit**: No known vulnerabilities. Workspace packages (`gifts`, `metar-*`) skipped — expected.
- **gitleaks** (`--no-git`): No leaks in working tree (~1.08 GB scanned).
- **Dangerous patterns** (`eval`/`exec` in `apps/`): None.
- **packages/gifts/gifts/common/tpg.py**: Pre-existing parser-generator `eval`/`exec` (upstream GIFTs); not introduced by S001.

### Cross-file

- **F401/F841**: 1 hit — `F841` unused `test_cases` in `apps/backend/scripts/generate_test_data.py:210`. File is outside `PY_LINT` scope in Makefile; not caught by `make lint`.

### Template conformance (`static+api`)

| Check | Result |
|-------|--------|
| `apps/backend/` API | OK |
| `apps/frontend/` static | OK — S001 changes confined here + `apps/e2e/` |
| `packages/auth/` library | OK — no changes |
| `packages/gifts/` | OK — no changes |
| `vendor/schemas/*` read-only | OK — untouched |
| `.github/workflows/ci-cd.yml` | OK |

### Connectivity (stage 09)

| Tier | Status | Notes |
|------|--------|-------|
| H0c | PASS | 6/6 unit CORS tests |
| H0i | PASS | 82/82 integration tests (in-process, no docker required for pytest subset) |
| H4–H5 live | SKIPPED | `LIVE_*` / `STAGING_*` unset in this environment |
| Artifacts present | OK | `scripts/deploy/verify_connectivity.sh`, `tests/smoke/test_staging_connectivity.py` |

Prior full-repo live QA (2026-06-22, `docs/qa-report.md`) verified H3–H6 green against Render URLs. S001 is frontend-only; no CORS or API contract changes expected.

---

## Findings for 11-verify-impl

| ID | Severity | Finding | Suggested action |
|----|----------|---------|------------------|
| QA-010 | Advisory | S001 implementation **uncommitted** on `feat/S001-convert-send-buttons` (~447 LOC delta) | User commit + PR before merge |
| QA-011 | Advisory | `make test-integration` exits 1 locally: backend smoke subset hits **28% coverage** vs 98% gate after main integration tests pass | Use alt ports (`METAR_BACKEND_HOST_PORT=18010`) if 18000/18001 busy; or run integration pytest directly (82 passed). CI job uses separate coverage targets — unaffected |
| QA-012 | Advisory | H4–H5 live connectivity not re-run this session | Run `make test-live-connectivity` before deploy signoff; see `docs/qa-report.md` for prior green run |
| QA-013 | Advisory | F841 in `apps/backend/scripts/generate_test_data.py` | Fix or exclude scripts from F841 sweep (pre-existing) |
| QA-014 | Advisory | `eval`/`exec` in `packages/gifts/gifts/common/tpg.py` | Document as upstream; no S001 action |
| QA-015 | Advisory | `docs/context/convert-send-buttons.md` §Executive Summary still says "Convert&Send is not implemented" | Update context doc status post-build (doc drift only) |

---

## Phase / execution-plan alignment

- **EV-001 scope**: F1 UI only — matches issue #656 and evolve decisions R1–R3.
- **Out of scope confirmed**: #555 auto-clear and error log preview — not in diff.
- **Next pipeline stage**: **10-e2e** (delta Playwright for Convert&Send journey).
- **Deploy gate**: Pending — requires commit, PR, and live H4–H5 on staging/production per `docs/deploy.md`.

---

## Handoff

**11-verify-impl** should:

1. Confirm QA-010 (commit/PR) with user.
2. Walk through issue #656 acceptance table above.
3. Defer or run QA-012 live connectivity before deploy.
4. Optionally refresh context doc (QA-015).

Do not re-run full 09 unless codebase changes materially after this report date.
