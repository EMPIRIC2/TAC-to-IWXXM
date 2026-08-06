# Evolve Plan Card

> Cycle: EV-039 | Session: S047-sql-ingest-live-e2e | Updated: 2026-08-06

## Goal

Live-verify F16 SQL BYOC upload against local Postgres, MySQL, SQL Server, and SQLite via
Playwright, with mandatory teardown across integration, e2e, and local harnesses.

## Features

- F16 — Dissemination drawer + multi-DB BYOC URI upload (deepen) — [Corpus: product §F16]

## In / out of scope

- In: Compose profile for PG/MySQL/SQL Server; SQLite file path; live Playwright preflight+send;
  teardown audit/fix for integration + e2e + local; test-plan / journey / tech-spec deltas
- Out: New vendors; live WIS2/EDIS/F19; prod SQL containers; new Fn; UI preview this cycle

## Preset + routing

- Preset: **Standard**
- Stages (ordered): `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`
- Skip: `03`, `06` (unless later need)

## Next child stage

**07-build** — M1 T1.1 (teardown contract test); then T1.2–T1.5. 06 skipped.

## Risks / open decisions

- Local allowlist: `localhost` / `127.0.0.0/8` in harness recipe (T1.4) — [Corpus: adr/ADR-030]
- SQL Server: required **local**; CI skippable / LIVE opt-in (`D-S047-04` Q4)
- Mocked H6′ stays separate from TC-F16-LIVE (AC3)
- `F16_LIVE_SQL` off when `CI=true` (S05.M2) — implement in T1.3
