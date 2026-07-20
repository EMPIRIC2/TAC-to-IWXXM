# Phase A checkpoint — EV-011 / S015

**Date**: 2026-07-19  
**Phase**: A (Product) — 01-requirements complete; 02-verify-plan next

## Digest

| Field | Value |
|-------|--------|
| Cycle | EV-011 — METAR lint issue registry + #732 quality |
| Features | **F15** (new); deepen **F6/F12**; SPECI adjacency in UJ-024 |
| Stages run | 00-context ✅; 01-requirements ✅ |
| Specs touched | feature-list, spec, api-contract, user-journeys, test-plan, COVERAGE_MATRIX, ADR-028, research catalog |
| Branch | `evolve/EV-011-metar-lint-quality` |
| Code | Docs only so far; no implementation commits yet |
| Tests | not run (planning) |
| Smokes | not run |

### What changed (plain language)

We scoped a maintainable `tac-validate` **issue registry** (INFO/WARNING/ERROR) under F15,
with stable public codes (ADR-028). METAR quality work from #732 includes golden
convert→XSD+Schematron, negative fixtures, research themes R1–R8, and **explicit SPECI
adjacency**. HTTP lint-tac response shape stays the same — only registry-backed codes grow.

### Your review

- Does behavior match what you asked for?
- Any acceptance scenario missing before 02-verify-plan?
