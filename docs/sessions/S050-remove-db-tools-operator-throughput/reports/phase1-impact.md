# Phase 1 — Fn allocation + impact (EV-042 / S050)

**Date:** 2026-08-07  
**Proceed:** D-S050-proceed = option 1  
**Corpus:** [Corpus: product §F7], [Corpus: product §F16], [Corpus: product §F33],
[Corpus: system-spec], [Corpus: api], [Corpus: tests], [Corpus: adr/ADR-029]

## Features

| Id | Mode | Scope |
|----|------|-------|
| F16 | deepen | UI-hide Postgres/MySQL/SQL Server/SQLite in Dissemination drawer; default sink WIS2 or last non-DB; API/adapters retained for harness; restore on #898 |
| F7 | deepen | Result queue + keyboard next/prev/Enter; batch multi-select convert/validate/disseminate; improvements pack |
| F33 | **new Planned** | Secure mass multi-file + folder/zip ingest; auth; caps; sniff/zip-bomb; progress + per-file errors |

## Routing

Standard (approved): `00→16→01→02→04→05→07→08→09→10→11→12→13` (skip 03/06 unless needed)

## Next

01-requirements delta interview for numeric caps, default sink choice, UJ/TC IDs, API shapes.
