# Build Plan Card — S057 / EV-048

> Updated: 2026-08-08

## Goal

Strip internal planning citations from operator UI and public OpenAPI/error surfaces;
add automated OpenAPI + FE string-catalog guards. [#951]

## Out of scope

Source comments; test names/docstrings; standing `docs/` / ADRs; commit/PR corpus rules;
staging/prod deploy (12/13 waived).

## Milestones

1. **M1** — Red guards + audit report (T1.1–T1.3)
2. **M2** — Strip OpenAPI Field/Form + route docstrings (T2.1–T2.3)
3. **M3** — FE catalog scanner + optional UJ-055 e2e (T3.1–T3.3)

## First batch (07)

T1.1 → T1.2 → T1.3 → T2.* → T3.* (TDD: red guards before strip).

## Guard (locked)

Base + `TC-*` + `E##-##` + `#NNN` (`D-S057-04-guard-ext=1`). Duplicate pattern
lists in BE pytest + FE Vitest OK (S5.M1 default).

## Corpus

[Corpus: product §F7] [Corpus: product §F21] [Corpus: api] [Corpus: tests]
