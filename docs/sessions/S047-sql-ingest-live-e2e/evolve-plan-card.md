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

**07-build** — **M2 T2.1 done** (red LIVE stubs); next **T2.2** (implement live e2e) + **T2.3** (write asserts, parallel).

## Risks / open decisions

- Playwright file `uj027-f16-live-sql.e2e.spec.ts` has T2.1 red stubs; T2.2 fills live UI flow
- Write-assert helpers in Python (S05.M3) — T2.3
- SQL Server: required **local**; CI skippable (`D-S047-04` Q4)
