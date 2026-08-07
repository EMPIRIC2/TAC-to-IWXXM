# QA Report — S050 / EV-042 (09-qa)

> Generated: 2026-08-07  
> Scope: delta — F33 + deepen F7 / F16–F19 (hide destinations, mass ingest, work queue)  
> Branch: `evolve/EV-042-remove-db-tools-operator-throughput` @ `6bc756ef`  
> Mode: delta  
> Corpus: [Corpus: product §F7/F16–F19/F33] [Corpus: tests] [Corpus: journeys §UJ-051..053]
> [Corpus: api] [Corpus: tech-spec]

```text
QA Results:
  Lint:           PASS — 0 issues (ruff + eslint)
  Format:         PASS — 0 files (ruff format + prettier)
  Typecheck:      PASS — 0 errors (17 pre-existing basedpyright warnings in tac2iwxxm iwxxm_us)
  Tests (Python): PASS — H0c 6/6; H0i 10/10; TC-F33 20/20; tip CI green
  Tests (FE):     PASS — Vitest 793 passed / 4 skipped (88 files); audit:ci 0 vulns
  Security:       PASS — pip-audit 0; FE audit 0; no pickle.loads/eval/exec in app packages
  Cross-file:     PASS — F401/F841 clean on backend + dissemination
  Dependencies:   advisory — SUPABASE_SERVICE_ROLE_KEY without SUPABASE_SECRET_KEY (env-check)
  Template:       PASS — apps/{backend,frontend,worker} + packages layout; no modal under apps/
  Data / Modal:   N/A — no Modal / data-staging assets in this cycle
  Connectivity:   PASS (local H0c/H0i); advisory — live H4–H5 deferred to 13
```

## Overall: **pass_with_advisories**

### Blocking

| Check | Status | Evidence |
|-------|--------|----------|
| Lint / format | PASS | `make lint` / `make format-check` |
| Typecheck | PASS | `make typecheck` — 0 errors |
| H0c CORS | PASS | `tests/unit/test_cors_policy.py` 6/6 |
| H0i (incl. mass ingest OPTIONS) | PASS | `apps/backend/tests/integration/test_h0i_connectivity.py` 10/10 |
| TC-F33 unit | PASS | guards + auth 20/20 |
| Frontend Vitest | PASS | 793 passed, 4 skipped |
| Security (pip-audit + FE audit) | PASS | 0 known vulns |
| Tip CI/CD | PASS | [31189257580](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31189257580) @ `6bc756ef` |

### Advisories (QA-IDs for 11-verify-impl)

| ID | Finding | Severity | Suggested action |
|----|---------|----------|------------------|
| QA-001 | Live H4–H5 (`LIVE_API_URL` / `LIVE_FRONTEND_URL`) unset locally — mass-route live CORS not re-run in 09 | advisory | Exercise at **13-deploy-smoke** / `make test-live-connectivity` |
| QA-002 | Host `.env` may still set `PLAYWRIGHT_BASE_URL=:5173` (S047 residual); UJ-051 suite needs explicit `:18000` | advisory | Override in Makefile / document; do not rely on bare `npx playwright` |
| QA-003 | `env-check` warns `SUPABASE_SERVICE_ROLE_KEY` without `SUPABASE_SECRET_KEY` | advisory | Migrate to canonical name (pre-existing) |
| QA-004 | Operator UJ-027–030 Playwright skipped until #898; Convert&Send E2E skipped | advisory | Track restore in #898 |
| QA-005 | Vitest **lines** threshold 95→94 (EV-042 note from 08) | advisory | Accept for cycle or recover coverage in follow-up |
| QA-006 | SlowAPI `HTTP_413_REQUEST_ENTITY_TOO_LARGE` deprecation warnings on mass-ingest cap tests | advisory | Upstream / alias when convenient |

### EV-042 acceptance alignment (delta)

| AC | Status in QA |
|----|----------------|
| AC1 destinations hidden | Covered by Vitest + Playwright UJ-053 |
| AC2 dissemination API retained | Dissemination unit CI green; operator UI skipped |
| AC3 queue / keyboard / batch | Vitest + Playwright UJ-052 |
| AC4–AC5 F33 auth + caps | TC-F33 unit + Playwright guest/auth paths |
| AC6 UJ + H4–H5 mapped | Local H0i/H4 wiring + Playwright; **live** H4–H5 → 13 |
| AC7 #898 restore track | Documented; not in-cycle |

### Commands run (reproducible)

```bash
make format-check
make lint
make typecheck
uv run pytest tests/unit/test_cors_policy.py -q --no-cov
cd apps/backend && uv run pytest tests/integration/test_h0i_connectivity.py \
  tests/unit/test_tc_f33_mass_ingest_guards.py \
  tests/unit/test_tc_f33_mass_ingest_auth.py -q --no-cov
pnpm --filter @metar/frontend exec vitest run
pnpm --filter @metar/frontend run audit:ci
uv tool run pip-audit -r <(uv export --frozen --no-dev) --no-deps \
  $(while read id; do echo --ignore-vuln $id; done < audit/pip-audit-ignore.txt)
# Prior M4: PLAYWRIGHT_BASE_URL=http://localhost:18000 PLAYWRIGHT_SKIP_WEBSERVER=1 \
#   npx playwright test uj051-053-ev042-mass-queue.e2e.spec.ts  → 6/6
```

### Next

1. **10-e2e** (Standard Phase D)  
2. **11-verify-impl** after 09+10  
3. Live H4–H5 at **13** (QA-001)
