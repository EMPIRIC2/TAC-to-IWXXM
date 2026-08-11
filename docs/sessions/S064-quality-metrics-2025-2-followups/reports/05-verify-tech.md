# 05-verify-tech — S064 / EV-055 (draft — awaiting Gate B)

**Status**: **in_progress** — statements ready for review  
**Date**: 2026-08-11  
**Mode**: delta  
**Plan approval**: `D-S064-04-plan=1`  
**Corpus**: [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13]
[Corpus: journeys §UJ-056] [Corpus: tests] [Corpus: api] [Corpus: decisions §EV-055]

## Documents audited

| # | Document | Criticality |
|---|----------|-------------|
| 1 | `reports/execution-plan.md` | highest |
| 2 | `build-plan-card.md` | highest (plan-readiness) |
| 3 | `docs/api-contract.md` (C14N match_status) | high |
| 4 | `docs/feature-list.md` (F7.q / F2 / F13 EV-055) | medium |
| 5 | `docs/user-journeys.md` (UJ-056) | medium |
| 6 | `docs/test-plan.md` (TC-EV055*) | medium |
| 7 | `docs/decisions/evolve-decisions.md` §EV-055 | medium |
| 8 | `docs/dependency-inventory.md` | medium (lxml; no new npm) |

## Plan-readiness

| Check | Result |
|-------|--------|
| Build Plan Card present | PASS |
| Card milestones M1–M5 ⊆ execution plan | PASS |
| In-scope M1 IDs T1.1–T1.4 ∈ Task Tracking | PASS |
| Spec Source on every task | PASS |
| Task count **17** | PASS |
| TDD within M (Test before Impl) | PASS (T2.3 combined Test/Impl noted as M2) |
| Card ↔ EP parity | PASS |

## High confidence (auto-approve — Gate A + `D-S064-04-plan=1`)

| ID | Statement | Source |
|----|-----------|--------|
| H1 | Always W3C C14N for match/diff | `D-S064-c14n=1` |
| H2 | #980 Schematron enable hard | `D-S064-sch-hard=1` |
| H3 | #979 SCHEMA_IMPORT fix hard | `D-S064-xsd-hard=1` |
| H4 | Panes default normalized; override → raw | `D-S064-gateA-M2` |
| H5 | Shared generator + FE normalize semantics | `D-S064-gateA-M1` |
| H6 | Regenerate corpus_metrics | `D-S064-regen=1` |
| H7 | F2/F13 engine-in; operator surface = Quality metrics | `D-S064-engine=1` |
| H8 | AC1–AC7 ↔ TC-EV055-001..007; UJ-056 deepen | product + tests |
| H9 | Milestone order M1 engine → M2 C14N → M3 regen → M4 FE → M5 E2E | `D-S064-m-order` / 04 approve |
| H10 | No new CORS tasks; H4–H5 via 12/13 | `D-S064-connectivity` |
| H11 | Vendor schemas read-only; no #836 redo; PR → stage | OOS / route |

## Medium confidence (user review)

| ID | Statement | Why medium |
|----|-----------|------------|
| M1 | Python C14N via **existing lxml** in `packages/shared`; FE via **local TS** exclusive-C14N; **no new npm** | Inferred implementation; not interviewed in isolation |
| M2 | Short **ADR**: quality-metrics C14N ≠ ADR-032 `canonicalize_xml` (ADR-032 stays for other callers) | Agent-proposed hygiene |
| M3 | M1 engine-first is correct even if C14N could ship earlier | Risk-first inference; user approved in 04 batch |
| M4 | Backend `schematron_validator` / `xsd_validator` parity tasks under T1.2/T1.4 are in scope | Engine-in allowed; parity not separately ticketed |
| M5 | If native Schematron enable is impossible, **block/re-scope** (not soft-close) | Matches Gate A hard rule + evolve risk note |

## Low confidence

| ID | Statement | Why low |
|----|-----------|---------|
| L1 | Native build always available in local/CI for T1.2 | Environment assumption — CI already builds F13, but local may skip |

## Consistency checklist (delta)

| Check | Result | Notes |
|-------|--------|-------|
| F7.q AC1–AC7 → tasks | PASS | M2–M5 cover AC1–3,6–7; M1 covers AC4–5 |
| F2/F13 #980/#979 → M1 | PASS | |
| UJ-056 / TC-EV055 map | PASS | |
| api-contract C14N | PASS | EP aligns |
| No circular deps | PASS | T3.2 waits T1.2+T1.4+T3.1 |
| No new npm vs inventory | PASS | pending M1 confirm |
| Connectivity Playwright + H4–H5 handoff | PASS | T5.1 + 12/13 |
| Card ↔ EP M1 batch | PASS | |
| Scope / OOS | PASS | |
| ADR-032 not silently replaced globally | PASS | M2 ADR + OOS |

## Gate B

**Pending** — approve medium/low below → `D-S064-05=1`.

## Next

**07-build** M1 after Gate B PASS (06 skipped).
