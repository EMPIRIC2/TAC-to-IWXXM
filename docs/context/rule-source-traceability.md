# Scoped context — rule-source-traceability (S043 / EV-035)

**Mode:** scoped · **Session:** S043-rule-source-traceability · **Cycle:** EV-035  
**Date:** 2026-08-05

## Goal

Durable **doc → rule → source** traceability for the full TAC→IWXXM stack, with
automated asserts so cite drift fails CI. Raise unfindable sources to the operator.

## Existing inventory (baseline)

| Layer | Location | Notes |
|-------|----------|-------|
| Canonicals | `docs/domain/TAC_VALIDATION.md`, `IWXXM_CONVERSION.md`, `IWXXM_VALIDATION.md` | Functional SoT |
| URL catalog | `docs/domain/rules/RULE_SOURCE_URLS.md` | Master URLs |
| Coverage | `docs/domain/rules/COVERAGE_MATRIX.md` | Product × role; G1–G7; ⚠/❌ gaps |
| Lint codes | `docs/domain/rules/ISSUE_CATALOG.{md,json}` | Theme tags; thin normative URLs |
| Digs | 25× `docs/domain/mining/*-mining-notes.md` | Transitory; promote durable cites |
| Catalog drift tests | `packages/tac-validate/tests/test_tc_f15_001_*` | Registry ↔ ISSUE_CATALOG only |

## Known soft spots (raise during audit)

- VONA encode: Guidance **silent** (cookbook + XSD/SCH)
- US REMARKS encode cells often ⚠ in coverage matrix
- Bulletin/AHL non-METAR family gaps
- Many `ISSUE_CATALOG` codes cite research themes (`A3-2`, `R8`) without a full
  `RULE_SOURCE_URLS` row linkage
- `docs/domain/**` not in minimal CORPUS — cite `[docs/domain/…]`; AskQuestion if F33
  registry should become a CORPUS member

## Proposed deliverable (no new Fn — G1=2)

Standing **rule↔source provenance map** under `docs/domain/rules/`
(`PROVENANCE_MAP.md` + machine-checkable twin) —
`rule_id | product | role | source_url | dig | status(ok|gap|paywall|N/A)` —
plus CI tests with dense asserts per cited/revisited rule. Deepens **F6 / F12 / F15 / F2**.

## Non-goals

UI provenance UX; vendor schema hand-edits; closing all #846 children here.
