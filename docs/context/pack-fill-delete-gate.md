# Context — pack fill + delete-gate (EV-pack-fill-delete-gate)

**Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-pack-fill-delete-gate`  
**Corpus:** [Corpus: product §F6] [Corpus: product §F9] [Corpus: adr/ADR-045] [Corpus: system-spec] [Corpus: tests]  
**Issue:** [#1214](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1214)  
**Prior:** EV-pack-ir-convert-wire / #1212 / merged PR #1213 / ADR-045 amend 2026-09-20

## Problem

METAR/SPECI packs and pack-IR convert path landed on `stage` (#1213). Remaining ADR-045 core packs are still empty shells (id+layout only). Convert for TAF / SIGMET family / label-field products still parses only via legacy `products/*.py`. The delete-gate stayed closed in #1212; this cycle reopens it **selectively** when byte-identical goldens pass.

## Current code (2026-09-20, post-#1213)

| Piece | Location | State |
|---|---|---|
| Builtin YAML | `tac-decoding/.../data/packs/` | `metar.yaml`, `speci.yaml` only |
| `_BUILTINS` | `packs.py` | All core ids + layouts; WAFS/QVACI stubs |
| Pack IR map | `tac2iwxxm/pack_ir_map.py` | METAR/SPECI; **still calls `parse_metar_speci`** for slot rebuild |
| IR source default | `ir_source.py` | Pack default only for METAR/SPECI |
| Legacy parsers | `products/{metar_speci,taf,sigmet_airmet,vaa_tca,swxa,vona}.py` | Still present; non-METAR/SPECI SoT for XML |
| Boundary | `test_no_tac2iwxxm_import` | Enforced |

## This cycle intent

1. **A — Fill + wire** all core packs (TAF, ordinary/VA/TC SIGMET, AIRMET, VAA, TCA, SWXA, VONA); keep METAR/SPECI.
2. **B — Delete-gate** — remove legacy parser modules/dead paths only where vendor XML is byte-identical on every existing pin; keep failures.
3. **Shared modules** — `metar_speci.py`, `sigmet_airmet.py`, `vaa_tca.py` need all-or-surgical rules.
4. **Unblock delete** — pack_ir_map must stop depending on legacy parsers for products we delete.

## Coverage peers (locked — D-PFDG-01 stricter)

| Product | In-bar peers (existing vendor examples) | Out of bar |
|---|---|---|
| TAF | `taf-A5-1`, `taf-A5-2` | `taf-NIL-collect`, `taf-translation-failed` |
| SIGMET | `sigmet-A6-1a-TS`, **`sigmet-A6-1b-CNL`** | translation-failed / collect |
| VA SIGMET | `sigmet-VA-EGGX`, **`sigmet-multi-location-VA`** | — |
| TC SIGMET | `sigmet-A6-2-TC` | — |
| AIRMET | `airmet-A6-1a-TS` | translation-failed |
| VAA | `va-advisory-A7-2` (2025-2) / `va-advisory-A2-1` (2023-1) | translation-failed |
| TCA | `tc-advisory-A2-2` | translation-failed |
| SWXA | `spacewx-A7-3` (+ **`_alternate`**), `spacewx-A2-3` on older pins | failed |
| VONA | `vona-A7-1` (where present) | — |
| METAR/SPECI | existing #1213 bar | unchanged |

Pins: every profile pin that already has the example (`2023-1`, `2025-2`, `3.0.0` as applicable).

## Must not break

Vendor XML byte identity; decode wire shape; `product=sigmet` single enum; shims; decode↛tac2iwxxm; import graph after partial deletes.

## Non-goals

Package merge; WAFS/QVACI full grammars; in-app pack editor; new WMO fetches; soft semantic compare; UI/H4–H5.

## F107 checkpoint

Session-open retrieve: `no_matches`. Historical retrieve: generic FailureMode `fm-recurring-arch` (session-store drift) — **adopt** (already using session-store). Spec question on RAG gates — **waive** (wrong domain).

## Downstream docs to delta

`docs/feature-list.md`, `docs/spec.md`, `docs/test-plan.md`, `docs/config-spec.md` (if IR source defaults expand), ADR-045 amend (delete-gate reopen), `docs/decisions/ev-pack-fill-delete-gate.md`, possibly `docs/api-contract.md` (library-only note).
