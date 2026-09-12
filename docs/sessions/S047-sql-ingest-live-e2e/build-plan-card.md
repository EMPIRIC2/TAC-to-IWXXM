# Build Plan Card

> Session: S047-sql-ingest-live-e2e | Updated: 2026-08-06 | Active: Phase 1 / M2 complete → 08

## Goal (one sentence)

Implement TC-F16-LIVE Playwright (no route mocks) with async-driver write assertions and teardown audit.

## Constraints

- Deepen F16 only — [Corpus: product §F16] [Corpus: tests] TC-F16-LIVE
- M1 complete (teardown + harness + tech-spec recipe)
- Write assert via Python async drivers (S05.M3 / Q2)
- Branch: `evolve/EV-039-sql-ingest-live-e2e`

## In scope (this batch — M2)

- [x] T2.1 — Test — TC-F16-LIVE-001..004 red stubs/markers — Spec: test-plan TC-F16-LIVE
- [x] T2.2 — Code — live e2e spec `uj027-f16-live-sql.e2e.spec.ts` — Spec: UJ-027; AC3
- [x] T2.3 — Code — write-assertion helpers (async drivers) — Spec: AC2; Q2
- [x] T2.4 — Test — teardown audit Testcontainers + SQLite temps — Spec: AC5/AC6
- [x] T2.5 — Docs — session teardown audit report — Spec: AC6

## Out of scope (explicit)

- Changing mocked H6′ `uj027-030-…` behavior
- WIS2/EDIS/F19 live; prod SQL

## Dependencies / blockers

- Prior: M1 T1.1–T1.5 **completed**
- Data: Compose images; ODBC for LIVE-003 assert

## Acceptance for this batch

- [ ] LIVE-001..004 green locally (CI opt-in / MSSQL skippable)
- [ ] Mocked H6′ still green
- [x] No orphan containers/volumes/SQLite temps (audit + skip path)
