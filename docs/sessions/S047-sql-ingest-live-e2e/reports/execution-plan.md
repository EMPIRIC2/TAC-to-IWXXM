# Execution Plan — S047 / EV-039 (F16 live SQL e2e + teardown)

> **Status**: **approved** (`D-S047-04-plan`=1) — awaiting Gate B (`05-verify-tech`)  
> **Generated**: 2026-08-06  
> **Skill**: 04-tech-plan (delta)  
> **Branch**: `evolve/EV-039-sql-ingest-live-e2e`  
> **Evolve cycle**: EV-039 · deepen **F16**  
> **Specs**: [Corpus: product §F16], [Corpus: system-spec §F16], [Corpus: journeys §UJ-027],
> [Corpus: tests] TC-F16-LIVE-001..004, [Corpus: tech-spec] mock-byoc,
> [Corpus: adr/ADR-029], [Corpus: adr/ADR-030], [Corpus: decisions] EV-039

## Current State

| Field | Value |
|-------|-------|
| **Active phase** | Phase 1: Live local SQL e2e |
| **Active milestone** | M1: Teardown harden + harness |
| **Active task** | T1.4 |
| **Tasks completed** | 3 / 10 |
| **Last updated** | 2026-08-06 |
| **Build Plan Card** | `docs/sessions/S047-sql-ingest-live-e2e/build-plan-card.md` |

## Tech decisions locked (`D-S047-04` — chat `Q1:1 Q2:1 Q3:1+3 Q4:1+2+3(local only)`)

| ID | Topic | Decision |
|----|-------|----------|
| Q1 | Teardown (S02.M1) | `compose … --profile mock-byoc down -v --remove-orphans` + post-check no named containers/volumes |
| Q2 | Write assert (S02.M4) | After UI success, query DB via async drivers (reuse fixture URIs / dissemination engines) |
| Q3 | Harness (S02.M2) | Dedicated `make test-e2e-f16-live-sql` **and** `F16_LIVE_SQL=1` flag on `test-live-e2e` |
| Q4 | LIVE vs prod / CI (S02.M5) | **Local:** LIVE in `make test-live` + **all four** dialects required. **CI:** opt-in; SQL Server skippable; LIVE not on default CI path |

## Tech Stack Summary (unchanged baseline)

| Category | Choice | Source |
|----------|--------|--------|
| Template | `static+api+worker` | workflow-state §template |
| Package | `packages/dissemination` | ADR-030 |
| Compose | `docker-compose.mock-byoc.yml` profile `mock-byoc` | tech-spec; F16-R3 |
| E2E | Playwright (`apps/e2e/`) | UJ-027; TC-F16-LIVE |
| Allowlist | `DISSEMINATION_EGRESS_ALLOWLIST` fail-closed | ADR-029/030 |
| Deploy | No new prod SQL services | F16-R9 OOS |

## Data Dependencies

| Asset | Staging | Needed By |
|-------|---------|-----------|
| Docker images: postgres:16, mysql:8.4, mssql/server:2022 | pull on `compose-mock-byoc-up` | M1–M2 |
| ODBC (SQL Server client) for write assert | local/CI skip path if missing | T2.3 LIVE-003 |
| Fixtures `mock-byoc-destinations.json` | staged (S019) | T2.2–T2.3 |

## Implementation Phases

### Phase 1: Live local SQL e2e + teardown

**Objective**: Harden Compose teardown; wire local live Playwright harness; assert DB writes; audit teardown layers.  
**Entry gate**: Execution plan + Build Plan Card approved (`D-S047-04-plan`); Gate A PASS.  
**Exit gate**: AC1–AC7 evidence; TC-F16-LIVE-001..004 green locally (CI opt-in OK); no orphan containers/volumes/SQLite temps.

`evolve_cycle_id: EV-039` · `feature_ids: []` · `deepen: [F16]`

#### M1 — Teardown harden + harness wiring (S02.M1 / M2 / M5)

**Goal**: Reliable `compose-mock-byoc-down` and make/CI entry points for local LIVE.  
**Acceptance**: AC4 (Compose), AC7 (make/docs); local `test-live` includes LIVE when Compose available.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T1.1 | Test: after up→down, assert no `metar-iwxxm-byoc-*` containers/volumes | Test | **completed** | AC4; S02.M1; tech-spec mock-byoc | — | Docker |
| T1.2 | Harden `compose-mock-byoc-down` → `down -v --remove-orphans` (+ keep all-down path) | Config | **completed** | AC4; Makefile; docker-compose.mock-byoc.yml | T1.1 | — |
| T1.3 | Add `test-e2e-f16-live-sql`; `F16_LIVE_SQL=1` on `test-live-e2e`; local `test-live` includes LIVE | Config | **completed** | AC7; S02.M2/M5; Q3/Q4 | T1.2 | — |
| T1.4 | Local harness recipe: CORS + allowlist `localhost`/`127.0.0.0/8` for live API↔FE | Config | pending | ADR-030; env-contract; H4–H5 local | T1.3 | — |
| T1.5 | Docs: tech-spec make targets + CI opt-in / SQL Server skip note | Docs | pending | tech-spec §mock-byoc; AC7; Q4 | T1.3 | — |

###### Parallelizable

None in M1 (linear TDD: test → config → docs).

#### M2 — Live Playwright + write assertion + teardown audit (S02.M4 · AC2/AC5/AC6)

**Goal**: TC-F16-LIVE-001..004 without route mocks; DB row/blob assert; cleanup audit.  
**Acceptance**: AC2–AC3, AC5–AC6; mocked H6′ file unchanged and green.

| # | Task | Type | Status | Spec Source | Depends On | Data Deps |
|---|------|------|--------|-------------|------------|-----------|
| T2.1 | Red tests: TC-F16-LIVE-001..004 (live Playwright stubs / markers) | Test | pending | test-plan TC-F16-LIVE; UJ-027 | T1.4 | Compose |
| T2.2 | Live e2e spec (separate from `uj027-030-…` mocked H6′) | Code | pending | UJ-027 live; AC3 | T2.1 | Compose |
| T2.3 | Write-assertion helpers via async drivers (PG/MySQL/SQL Server/SQLite) | Code | pending | AC2; S02.M4; Q2 | T2.1 | Compose + ODBC for MSSQL |
| T2.4 | Teardown audit: Testcontainers fixtures + SQLite temp removal; fix gaps | Test | pending | AC5/AC6; LIVE-004 | T2.2, T2.3 | — |
| T2.5 | Session report: teardown audit results / waivers | Docs | pending | AC6; session reports | T2.4 | — |

###### Parallelizable

After T2.1: T2.2 and T2.3 can proceed in parallel (different files: e2e spec vs assert helpers).

#### Phase 1 Gate Check

- [ ] T1.* + T2.* completed
- [ ] `make compose-mock-byoc-down` leaves no orphans (T1.1 green)
- [ ] Local: `make test-e2e-f16-live-sql` (or `F16_LIVE_SQL=1` / local `test-live`) runs all four dialects
- [ ] CI docs: LIVE opt-in; SQL Server skippable
- [ ] Mocked H6′ still green (AC3)
- [ ] AC1–AC7 evidence in session report

## Connectivity (stage 04 deliverables — delta)

| Item | EV-039 action |
|------|----------------|
| CORS / `METAR_CORS_ORIGINS` | Local harness recipe in T1.4 (no new staging service) |
| `DISSEMINATION_EGRESS_ALLOWLIST` | Local includes `localhost`/`127.0.0.0/8` (already recommended); document for LIVE |
| H4–H5 | Local UI↔API only for LIVE suite — not Render prod SQL |
| Staging secrets matrix | No new keys; pointer in T1.5 if needed |

## Git Strategy

| Item | Value |
|------|-------|
| Branch | `evolve/EV-039-sql-ingest-live-e2e` |
| Commits | One task per commit `[T1.1]` … `[T2.5]` |
| PR | End of cycle to `main` (after 11–13 per routing) |

## Task Tracking

| Task | Milestone | Status | Blocked By |
|------|-----------|--------|------------|
| T1.1 | M1 | **completed** | — |
| T1.2 | M1 | **completed** | — |
| T1.3 | M1 | **completed** | — |
| T1.4 | M1 | pending | T1.3 |
| T1.5 | M1 | pending | T1.3 |
| T2.1 | M2 | pending | T1.4 |
| T2.2 | M2 | pending | T2.1 |
| T2.3 | M2 | pending | T2.1 |
| T2.4 | M2 | pending | T2.2, T2.3 |
| T2.5 | M2 | pending | T2.4 |

## Phase Gate Log

| Gate | Result | When | Notes |
|------|--------|------|-------|
| A→B (02) | **PASS** | 2026-08-06 | `D-S047-02-gate-a`=2 |
| Plan approve (04) | **PASS** | 2026-08-06 | `D-S047-04-plan`=1 |
| B→C (05) | **PASS** | 2026-08-06 | `D-S047-05-gate-b`=1 |
| C→D | pending | — | — |

## Out of scope (confirm)

- New vendors; live WIS2/EDIS/F19; production SQL containers; new Fn; UI preview
- Changing mocked H6′ behavior beyond keeping it separate/green
- Default CI requiring LIVE or all four dialects
