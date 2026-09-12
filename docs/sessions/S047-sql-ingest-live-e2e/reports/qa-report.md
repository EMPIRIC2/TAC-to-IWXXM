# QA Report — S047 / EV-039 (09-qa)

> Generated: 2026-08-06  
> Scope: deepen F16 — Docker LIVE harness + M1/M2  
> Branch: `evolve/EV-039-sql-ingest-live-e2e` @ `476c9c9d` (+ playwright unit fix)  
> Mode: delta  
> Corpus: [Corpus: product §F16] [Corpus: tests] [Corpus: tech-spec] [Corpus: adr/ADR-029]

```text
QA Results:
  Lint:           PASS — 0 issues
  Format:         PASS — 0 files
  Typecheck:      PASS — 0 errors (pre-existing basedpyright warnings in tac2iwxxm)
  Tests (Python): PASS — after TC-LIVE-004 config assert update; full make test-unit
  Tests (FE):     PASS — vitest + audit:ci (js-yaml >=4.3.1)
  Security:       PASS — gitleaks 0; pip-audit 0; frontend audit 0
  Cross-file:     PASS — unused-import gate via ruff
  Dependencies:   advisory — js-yaml pin landed in 476c9c9d (GHSA-5p4m-2wfm-xmqj)
  Template:       PASS — static+api+worker layout unchanged
  Data / Modal:   advisory — no Modal staging URLs in this cycle
  Connectivity:   PASS — H0c 6/6; tests/integration green
```

## Overall: **PASS** (pass_with_advisories)

### Blocking

| Check | Status |
|-------|--------|
| Lint / format / typecheck | PASS |
| H0c CORS | PASS |
| Integration (H0i sample `tests/integration`) | PASS |
| Unit suite | PASS (after `test_playwright_live_mode` update for `skipWebServer`) |
| Secrets / pip-audit / FE audit | PASS |

### Advisories (QA-IDs for 11-verify-impl)

| ID | Finding | Severity |
|----|---------|----------|
| QA-001 | SQL Server LIVE-003 skipped on Apple Silicon QEMU (`F16_SKIP_SQLSERVER=1`) | advisory |
| QA-002 | Host `.env` still has stale `PLAYWRIGHT_BASE_URL=:5173` — Makefile LIVE overrides to `:18000` | advisory (local env) |
| QA-003 | `SUPABASE_SERVICE_ROLE_KEY` without `SUPABASE_SECRET_KEY` warn from env-check | advisory (pre-existing) |
| QA-004 | H4–H5 staging URLs unset — not exercised this cycle (local Docker only) | advisory |

### Harness commits

- `476c9c9d` — js-yaml pin + Docker F16 LIVE harness (allowlist, Colima protect, URI rewrite, verification-report)
- Follow-up: `test_playwright_live_mode.py` asserts `skipWebServer` / `PLAYWRIGHT_SKIP_WEBSERVER`
