# E2E Behavior Report — 10-e2e (S070 / EV-060)

> Generated: 2026-08-18  
> Mechanism: Playwright Chromium vs local `:18000` / `:18001` + live API  
> Branch: `evolve/EV-060-converter-operator-bugs`  
> Corpus: [Corpus: journeys] [Corpus: tests] [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F2] [Corpus: product §F29] [Corpus: product §F31] [Corpus: api] [Corpus: decisions §EV-060]

## Summary

| Tier | Scope | Result |
|------|-------|--------|
| T0 | EV-060 unit/Vitest (see 09-qa) | PASS |
| T2 local browser + API | UJ-059..063 + TC-EV060-1006 | **13 passed / 1 failed** |
| T2 connectivity H4–H5 | staging frontend | **DEFERRED** → 12/13 |
| T3 live | staging/prod | **DEFERRED** → 13 / 15 |

**Overall (local T2 for EV-060):** **FAIL** — TC-EV060-1006-003 logout (see below). Converter journeys UJ-059..063 **PASS**.

## Journey matrix (delta)

| Journey | Spec | T0 | T2 local | T3 |
|---------|------|----|----------|----|
| UJ-059 AHL heading | `tc-ev060-uj059-063.e2e.spec.ts` | PASS (tac-validate + lint-tac) | **PASS** (3) | deferred H4–H5 |
| UJ-060 IWXXM product | same | PASS (backend TC-EV060-1003) | **PASS** (3) | deferred |
| UJ-061 Profile at top | same + Vitest 1002 | PASS | **PASS** (1) | deferred |
| UJ-062 Bulletin fields | same + Vitest 1005 | PASS | **PASS** (2) | deferred |
| UJ-063 log_level | same + backend 1004 | PASS | **PASS** (2) — control sent; API accepts DEBUG/ERROR | n/a (T0/T2 only) |
| UJ-003 / UJ-046 Auth | `tc-ev060-1006-auth.e2e.spec.ts` | — | **001/002 PASS; 003 FAIL** | deferred |
| UAT-003 | facilitated | — | **ACCEPTED** 2026-08-18 (`D-S070-uat003`) | — |

## Execution

Local `make-dev` was down; restarted (`D-S070-local-dev=4a`). FE `:18000` and API `:18001` `/health` both 200. `METAR_CONFIG_ENV=local`. `PLAYWRIGHT_SKIP_WEBSERVER=1`.

```bash
cd apps/e2e && \
  METAR_CONFIG_ENV=local \
  PLAYWRIGHT_SKIP_WEBSERVER=1 \
  PLAYWRIGHT_BASE_URL=http://localhost:18000 \
  PLAYWRIGHT_API_BASE_URL=http://localhost:18001 \
  pnpm exec playwright test \
    tc-ev060-uj059-063.e2e.spec.ts \
    tc-ev060-1006-auth.e2e.spec.ts
```

First run failed in `playwright.global-setup.ts` waiting on **`:5173`** (host `.env` residual — QA-001). Override to `:18000`/`:18001` is required.

Second run: **13 passed, 1 failed** (39.3s) before the logout assertion was tightened; UJ-059..063 all green. Re-run of 1006-003 after waiting for the scope menu: **`POST /auth/logout` → 404**.

## Journey details

### UJ-059 AHL bulletin — PASS

1. AHL mode convert shows bulletin summary (2 reports) — PASS  
2. `POST /api/v1/lint-tac` well-formed AHL: no `MISSING_PRODUCT_KEYWORD` / `MULTI_REPORT_BULLETIN` — PASS  
3. Malformed AHL: one bulletin `INVALID_AHL` — PASS  

### UJ-060 IWXXM product — PASS

1. Product IWXXM help + “Lint & validate”; F7.s Validate mode still enabled — PASS  
2. TAC text + `product=iwxxm` → `NOT_XML` — PASS  
3. Minimal XML + `product=iwxxm` lints without TAC keyword flood — PASS  

### UJ-061 Profile — PASS

Labeled Profile at converter top (`profile-type-select`); convert multipart includes `iwxxm_us`; conversion results region visible.

### UJ-062 Bulletin fields — PASS

Bulletin ID + Issuing Center visible without expanding parameters; convert sends `SAAA00` / `KWBC`; invalid `KW1C` shows issuing-center field error.

### UJ-063 log_level — PASS

`#param-log-level` DEBUG is sent on convert; live `POST /api/v1/convert` accepts DEBUG and ERROR (`<500`, 200 or 422). Verbosity/secret redaction remains T0 (`test_tc_ev060_1004_log_level.py`).

### TC-EV060-1006 Auth — mixed

| Case | Result |
|------|--------|
| 001 register (stubbed `/auth/register`, no production PII) | PASS |
| 002 login + reload persist (`E2E_USER_*` / `ADMIN_*`) | PASS |
| 003 logout → guest convert | **FAIL** |

**003 evidence:** FileConverter scoped logout POSTs `http://localhost:18001/auth/logout`. Local OpenAPI paths under `/auth` are only `/auth/login` and `/auth/me` (`packages/auth` router is login+me per ADR-033). Response **404** → `signOutWithScope` returns false → UI stays on **Logout options** with the scope menu open. Guest convert after logout did not run.

**[Contradiction]** Facilitated **UAT-003 ACCEPTED** (`D-S070-uat003`) vs T2 **404** on the same local converter. For 11-verify-impl: restore `POST /auth/logout`, change the FE not to require it, or waive 003 with rationale. 10-e2e did not change product code.

Register remains stubbed (no production PII). Persist used existing `E2E_USER_*` / `ADMIN_*`.

## Outcome

- Converter operator journeys **UJ-059..063: PASS** on local T2.  
- Auth **login persist: PASS**; **logout: FAIL** (missing `/auth/logout`).  
- Live H4–H5 stays **12/13**. UI preview stays **11** (`D-S070-e2`).  
- PR #1007 still OPEN → `stage`. Promote held.
