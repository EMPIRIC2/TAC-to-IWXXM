# 02-verify-plan audit — S016 / EV-012

**Date**: 2026-07-20  
**Mode**: delta (changed sections + cross-doc consistency)

## Inventory (delta focus)

| # | Document | Delta sections | Status |
|---|----------|----------------|--------|
| 1 | feature-list.md | F7 validation deepen | audited |
| 2 | spec.md | F7 input modes ADR-024 + validation pointer | audited |
| 3 | user-journeys.md | UJ-025 | audited |
| 4 | test-plan.md | UJ-025 map, TC-F7-007, input-modes gate, UI↔API row | audited |
| 5 | api-contract.md | convert-bulletin / ingest-collect 501 (unchanged) | consistent |
| 6 | ADR-024 | Accepted (unchanged) | consistent |
| 7 | acceptance-criteria.md | absent (N/A) | skip |

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec (F7 input modes) | PASS |
| Feature ↔ Journey (UJ-025) | PASS |
| Journey ↔ Test (UJ-025 ↔ TC-F7-007) | PASS |
| Feature ↔ Test | PASS |
| API contract ↔ ADR-024 / UJ-025 | PASS |
| Spec ↔ Config | N/A (no new params) |
| Naming (UJ-025 / TC-F7-007 / ADR-024) | PASS |
| Scope (no COLLECT extract; F7 Planned) | PASS |
| Connectivity H4–H5 in gate | PASS |
| H6 / H6′ lists UJ-025 | **FAIL** — see S2.1 |

## Auto-approved (high confidence)

| ID | Statement | Source |
|----|-----------|--------|
| S0.1 | Cycle is F7 validation only; no new Fn | E12-1 |
| S0.2 | COLLECT remains HTTP 501 placeholder UX | E12-1 / ADR-024 |
| S0.3 | Auto-switch on paste/upload is required (T3) | E12-3 |
| S0.4 | Vitest + Playwright T1–T4 + live staging all required | E12-2 |
| S0.5 | Include 13-deploy-smoke; lean skips 03–09, 11–12 | E12-4 / route-1 |
| S0.6 | F7 status remains Planned | E12-1 |
| S0.7 | UJ-025 / TC-F7-007 describe modes TAC / AHL / COLLECT | 01 delta / #730 |
| S0.8 | UJ-025 does not replace UJ-011 / H7 API gate | E12 scope / UJ-025 text |

**Auto-approved**: 8

## Pending user review

| ID | Conf | Category | Statement |
|----|------|----------|-----------|
| S2.1 | Low | Contradiction | H6 connectivity row omits UJ-025 while journey maps to H6′ |
| S2.2 | Medium | Ambiguity | T5/T6 “as coverage allows” vs E12-2 “all tests green” |
| S2.3 | Medium | Decision | New UJ-025 (vs extending UJ-013) is correct ID choice |

## Verdicts log

| ID | Verdict | Notes |
|----|---------|-------|
| S0.1–S0.8 | auto-approved | high confidence |
| S2.1 | approve + fix | H6 row includes UJ-025 (H6′) |
| S2.2 | modify | T1–T6 all hard gates (not T5/T6 best-effort) |
| S2.3 | approve | Keep UJ-025 |

## Gate result

**PASS** (fix-in-place applied). Phase A complete for lean route; next **10-e2e**.

