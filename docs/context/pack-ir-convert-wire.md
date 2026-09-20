# Context — pack IR convert wire (EV-pack-ir-convert-wire)

**Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-pack-ir-convert-wire`  
**Corpus:** [Corpus: product §F6] [Corpus: product §F9] [Corpus: adr/ADR-045] [Corpus: system-spec] [Corpus: tests]  
**Prior:** EV-configurable-tac-decode-packs / #1210 / merged PR #1211 / ADR-045

## Problem

#1211 shipped the shared pack engine and `convert_shadow` (pack match beside legacy; `pack_ir` next to `legacy_ir`). Builtin packs are still empty shells (`Pack(id, layout)` with no rules), so match is mostly residuals. Convert still emits XML only from legacy `products/*.py`. The real link — enrich packs + emit from pack IR — is not done. ADR-045 keeps packages separate on purpose.

## Current code (2026-09-20)

| Piece | Location | State |
|---|---|---|
| Builtin packs | `packages/tac-decoding/.../packs.py` `_BUILTINS` | ids + layouts only; `rules=()` |
| Match / NL | `tac_decoding.match`, `decode` | works; empty rules ⇒ residuals |
| Pack IR projection | `tac_decoding.ir.project_ir` | spans + residuals + context; not legacy slot IR |
| Shadow convert | `tac2iwxxm.shadow.convert_shadow` | legacy XML + optional `pack_ir` |
| Legacy parsers | `tac2iwxxm/products/*.py` | still source of truth for XML |
| Decode ↛ tac2iwxxm | tests `test_no_tac2iwxxm_import` | enforced |

## This cycle intent

1. **Fill packs** — METAR/SPECI first until vendor peers get real rule coverage.
2. **Wire convert to pack IR** — emit IWXXM from pack IR behind/beside legacy until goldens match.
3. **Delete gate closed** — no `products/*.py` removals; later EV when byte-identical on every pin.
4. **Keep packages separate** — engine vs emitter.

## Must not break

Vendor XML byte identity; `decode_tac` wire shape; `product=sigmet` single enum; shims; package boundary.

## Non-goals

Package merge; mass legacy delete; in-app pack editor; new WMO fetches; UI/H4–H5; WAFS/QVACI full grammars.

## Downstream docs to delta

`docs/feature-list.md` (F6/F9 deepen note), `docs/spec.md`, `docs/test-plan.md` (new TCs beyond TC-EV1210-*), possibly `docs/api-contract.md` (library-only if no HTTP change), ADR-045 amend only if tech locks change.
