# Execution plan — S019 / EV-014 (F16–F19 dissemination)

> **Status**: **approved** (2026-07-21) — Q34=A / D-S019-EV014-Q34A-04-approve;
> **05-verify-tech** PASS (D-S019-EV014-Q35A-05) — task count corrected to **29**  
> **Branch**: build off `main` @ `#753` merge (`3c9ee81`); prior plan branch
> `cursor/dissemination-upload-e25c` **merged**  
> **Evolve cycle**: EV-014  
> **Features**: F16, F17, F18, F19  
> **PR (04)**: [#753](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/753) MERGED  
> **Spec sources**: feature-list F16–F19; ADR-021/029/030; spec §F16–F19; UJ-027–030;
> TC-F16..F19; api-contract Dissemination; env-contract allowlist; E14-01..10

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase C — **07-build** M6 **complete** (T6.6 done via mock BYOC) |
| **Active milestone** | M6 — FE drawer + connectivity + verify |
| **Active task** | T6.6 (**completed** — D-S019-EV014-Q15-mock-waive) |
| **Blockers** | None for M6. Live destination BYOC **waived** in favor of mock/harness evidence. |
| **Tasks** | **29 / 29** completed |
| **Branch** | `cursor/s019-t66-deploy-smoke-151c` (PR #772) |
| **Last updated** | 2026-07-21 (mock BYOC unblock) |

## Tech Stack Summary

| Area | Choice | Source |
|------|--------|--------|
| Package | `packages/dissemination` (MIT; no FastAPI/Supabase) | E14-01 / ADR-030 |
| DB | SQLAlchemy 2 async + asyncpg / aiomysql / aioodbc / aiosqlite | E14-02 / E14-06 |
| API | `POST /api/v1/dissemination/preflight` + `/send` | E14-03 |
| HTTP encode | msgspec + pydantic OpenAPI aliases | E14-07 / ADR-026 |
| SSRF | ADR-029 + `DISSEMINATION_EGRESS_ALLOWLIST` | E14-08 |
| wis2box | Docker Compose / CI harness | E14-04 |
| EDIS | `aiosmtplib` | E14-05 |
| F19 | Sink adapters (AMHS/SWIM/AFS); staging required; live optional | E14-05 / S-EV014-M2 |
| Tests | Unit + Compose/Testcontainers + mocks; Playwright; live BYOC close gate | E14-09 |
| FE | Dissemination drawer this cycle; H4–H5 required | E14-10 |
| Deploy | Render API/static (existing); no Render wis2box service | E14-04 / E14-08 |

## Data Dependencies

| Asset | Staging | Needed By |
|-------|---------|-----------|
| Compose wis2box image/config | staged (T3.3 harness image) | T3.4 / TC-F17-001 |
| ODBC driver (CI/docs for SQL Server) | staged (skip-without-ODBC tests) | T2.6–T2.7 done |
| Live BYOC creds (operator) | cycle close only | TC-F16/17/18 live gates |

## Milestones & Tasks (TDD order)

`evolve_cycle_id: EV-014` · `feature_ids: [F16, F17, F18, F19]`

### M1 — Package scaffold + SSRF/allowlist (F16 foundation)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T1.1 | Test | Package layout + import smoke; no FastAPI/Supabase imports | ADR-030; plan-adherence | — | **completed** |
| T1.2 | Config | Add `packages/dissemination` workspace member + pyproject deps (sqlalchemy, asyncpg, aiomysql, aiosqlite, aioodbc, aiosmtplib, msgspec) | dependency-inventory; E14-06 | T1.1 | **completed** |
| T1.3 | Test | Allowlist parse + fail-closed when empty; DNS/private-range deny unit tests | ADR-029; TC-F16-002 | T1.2 | **completed** |
| T1.4 | Code | SSRF/allowlist helpers in package; env `DISSEMINATION_EGRESS_ALLOWLIST` | env-contract; E14-08 | T1.3 | **completed** |
| T1.5 | Config | `.env.example` + staging-secrets note; Makefile target for Compose stub (placeholder) | config-spec F16–F19 | T1.4 | **completed** |

### M2 — Multi-DB writer-contract + preflight/send API (F16)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T2.1 | Test | Writer-contract schema diff fixtures (PG/MySQL/SQLite); DDL create-if-missing | TC-F16-001/003; F16-R4 | T1.4 | **completed** |
| T2.2 | Code | Engine adapters + versioned writer-contract DDL | ADR-030; E14-02 | T2.1 | **completed** |
| T2.3 | Test | API tests: preflight/send msgspec shapes; secret redaction; handle memory-only; per-user rate-limit deny (ADR-029 §5) | api-contract; TC-F16-002; ADR-029 | T2.2 | **completed** |
| T2.4 | Code | Thin backend routers `/dissemination/preflight` + `/send` (+ rate limit) | api-contract; E14-03/07; ADR-029 | T2.3 | **completed** |
| T2.5 | Test | Compose/Testcontainers integration PG+MySQL+SQLite happy + mismatch | TC-F16-003; E14-09 | T2.4 | **completed** |
| T2.6 | Test | SQL Server path via aioodbc (CI skip if no ODBC; document) | E14-06; TC-F16-003 | T2.4 | **completed** |
| T2.7 | Docs | ODBC driver notes in deploy.md / package README | E14-06 | T2.6 | **completed** |

### M3 — WIS2 + Compose wis2box harness (F17)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T3.1 | Test | WIS2 sink adapter unit tests (mocked MQTT/HTTP) | TC-F17-001; E14-09 | T2.4 | **completed** |
| T3.2 | Code | WIS2 sink in `packages/dissemination` | F17; ADR-030 | T3.1 | **completed** |
| T3.3 | Config | `docker-compose` wis2box harness + CI service/job | E14-04; TC-F17-001 | T3.2 | **completed** |
| T3.4 | Test | Staging harness publish green (TC-F17-001) | UJ-028 | T3.3 | **completed** |

### M4 — EDIS SMTP (F18)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T4.1 | Test | EDIS message formatting + mocked aiosmtplib submit | TC-F18; E14-05/09 | T2.4 | **completed** |
| T4.2 | Code | EDIS sink + RTH header helpers | F18; #6 | T4.1 | **completed** |
| T4.3 | Test | Preflight connectivity check for SMTP params (no live send in CI) | TC-F18; E14-09 | T4.2 | **completed** |

### M5 — AMHS / SWIM / AFS adapters (F19)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T5.1 | Test | Adapter interface + staging stub behaviors | F19; S-EV014-M2 | T2.4 | **completed** |
| T5.2 | Code | AMHS/SWIM/AFS sink stubs + drawer-ready sink_type enums | ADR-030; E14-05 | T5.1 | **completed** |
| T5.3 | Test | Staging/test path green for each adapter (mocked transport OK) | TC-F19; E14-09 | T5.2 | **completed** |

### M6 — FE drawer + connectivity + verify (F16–F19 UI)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T6.1 | Test | Vitest: drawer sink chooser + preflight diff + block Send | TC-F16-001/004; UJ-027 | T2.4 | **completed** |
| T6.2 | Code | Dissemination drawer UI (URI, drag-drop, sink types) | F16–F19; E14-10 | T6.1 | **completed** |
| T6.3 | Test | Playwright UJ-027–030 smokes (H6′) | test-plan H6′ | T6.2, T3.4, T4.3, T5.3 | **completed** |
| T6.4 | Config | 08-verify-build — lint/typecheck/format/full suites | 08 | M1–M5, T6.2 | **completed** |
| T6.5 | Config | 12-verify-deploy checklist (allowlist + Compose harness) | 12; E14-08 | T6.4 | **completed** |
| T6.6 | Config | 13-deploy-smoke H1–H5 + H0c; live BYOC close gate evidence | 13; Q15/Q21; TC-F17-002 | T6.5 | **completed** (H0c/H1/H4/H5 PASS; #771 merged + live FE drawer; mock BYOC Postgres/WIS2/EDIS via `make test-mock-byoc-smoke` — D-S019-EV014-Q15-mock-waive; live H3 auth waived) |

### Stage 06 (before 07-build; optional tooling)

| Task | Type | Description | Spec Source | Depends On | Status |
|------|------|-------------|-------------|------------|--------|
| T0.1 | Config | 06-tech-tooling: coverage paths for `packages/dissemination`; CI Compose service hooks | 06; E14-09 | Plan approval | **completed** |

## Git Strategy

- Base: `main` @ `#753` (`3c9ee81`). Build branch: `cursor/<slug>-b45b` (or
  `evolve/EV-014-dissemination`) off `main` — do **not** reopen merged
  `cursor/dissemination-upload-e25c`.
- Atomic commits per task: `[T{n}.{m}] type: …`
- One logical PR for build; minor PRs per milestone optional

## Phase Gate Criteria (build)

| Gate | Criteria |
|------|----------|
| M1→M2 | Package importable; allowlist fail-closed tests green |
| M2→M3 | Preflight/send API green for PG+MySQL+SQLite |
| M3→M4 | TC-F17-001 harness green |
| M4→M5 | EDIS mocked path green |
| M5→M6 | F19 staging stubs green |
| C→D | M1–M6 tasks done; 08 pass |
| Cycle close | Live BYOC Postgres+WIS2+EDIS (Q15=A); F19 live optional waive |

## Approval

**Approved** 2026-07-21 — Q34=A (D-S019-EV014-Q34A-04-approve). 04-tech-plan complete.  
**05-verify-tech** PASS 2026-07-21 — D-S019-EV014-Q35A-05 (29 tasks; branch/ADR/matrix fixes).  
**06-tech-tooling** complete 2026-07-21 — D-S019-EV014-Q36A-06 (T0.1 coverage + Compose hooks).  
Next: Phase B checkpoint → **07-build** (M1 T1.1).
