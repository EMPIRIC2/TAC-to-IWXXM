# Scoped context — quality-residuals-831 (S037 / EV-030)

**Mode:** scoped · **Date:** 2026-08-02  
**Session:** S037-quality-residuals-831 · **Cycle:** EV-030  
**Issues:** [#831](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/831) · [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829) · [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820)

## Problem

S036 / EV-029 closed the eight-family umbrella (#823) with three deepen residuals:

1. **#831** — No unified parameterized matrix ensuring every lint/convert/validate rule has a
   fixed 5×4 case budget (happy / sad / edge-pass / edge-fail). Existing coverage is golden-
   and product-order heavy, not rule-inventory gated.
2. **#829** — TC SIGMET quality path shipped in M7 (#738 closed), but lacks a dedicated
   `tac-validate` TC pack (peer to VA), STNR/exceptional geometry negatives, and a catalog
   decision for `sigmet-A6-2-TC` sample-menu unlock (UJ-039 / ADR-032).
3. **#820** — F9 G4 intentionally left VAA/TCA decode residual-heavy; official peers still
   leave large residual spans after keyword decode.

## Prior art (do not restart)

| Artifact | Use |
|----------|-----|
| `docs/sessions/S036-…/reports/evolve-summary.md` | Residual table + close disposition |
| `docs/sessions/S036-…/reports/verification-report-m7.md` / `t7.4-738-closeout.md` | #829 scope boundary |
| `docs/domain/rules/COVERAGE_MATRIX.md` | Gap / menu tier cells |
| `packages/tac-validate/tests/test_tc_f15_*`, `test_tc_f20_*`, `test_tc_f23_*` | Family quality packs to peer |
| `Makefile` `test-tc-sigmet-quality` / annex3 product-order | TC convert→validate path |
| S034 / EV-027 + #815 closeout | VAA/TCA G4 allowlist intent for #820 |
| Issue #831 evaluation questions | Harness design must answer before bulk fixtures |

## Recommended work order

1. **#831 spike + design note** → runner API → pilot (METAR/SPECI lint+encode+validate)
2. **#829** deepen on top of M7 path (registry pack + STNR/OOS + menu tier)
3. **#820** decode deepen (structured labels / forecast hours; matrix updates)

## Resolutions (local)

| ID | Finding |
|----|---------|
| R1 | Session order locked: #831 → #829 → #820 (`D-S037-open` Q1=1) |
| R2 | Standard evolve routing; UI preview declined (catalog unlock without local UI pass) |
| R3 | Fn allocation deferred to 16-evolve Phase 1 — recommend **F29** matrix harness + deepen F23/F12/F2/F13/F9/F26/F27 |
| R4 | No network/Supabase in matrix harness (#831 non-goal) |

## Success (session-level)

- #831: written harness recommendation + runners + pilot filled or explicit `needs-fixture` inventory
- #829: acceptance checkboxes met or OOS with cite; issue closable or child-split
- #820: residual spans shrink / allowlist updated; issue closable or child-split
- Deploy smoke green if FE/API contracts change; else document waive
