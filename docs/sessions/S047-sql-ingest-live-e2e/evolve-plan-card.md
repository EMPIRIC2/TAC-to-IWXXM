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

**01-requirements** (delta) — draft F16 deepen ACs for live multi-DB upload + teardown
hygiene; cite [Corpus: product], [Corpus: tests], [Corpus: journeys], [Corpus: tech-spec].

## Risks / open decisions

- Local SSRF allowlist for compose service hostnames (test-only) vs existing
  `DISSEMINATION_EGRESS_ALLOWLIST` — [Corpus: adr/ADR-030]
- SQL Server image weight / CI flakiness — may mark opt-in profile while still required in
  local live suite
- Existing UJ-027 specs mock HTTP; live suite must be separate (not break mocked H6′ smokes)
