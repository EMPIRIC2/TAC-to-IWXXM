# Tech plan — EV-yaml-full-configurability (#1226)

**Session:** EV-yaml-full-configurability  
**Locked:** 2026-09-21 (intake + ADR-047 Proposed)  
**Gate:** documenting → implementing **closed** until verify + AskQuestion

[Corpus: product] [Corpus: adr/ADR-047] [Corpus: tech-spec] [Corpus: tests] [Corpus: decisions]

## Architecture

| Piece | Location |
|-------|----------|
| Emit map catalogs + overlays | `packages/tac2iwxxm` (new module; env TBD in Build) |
| Decode / TAC / IWXXM overlays | Existing packages + `scripts/overlays/preflight.py` |
| Matrix | `docs/domain/overlays/product-engine-matrix.md` |
| Templates | `packages/*/examples/` + starter kits (M1) |
| Pin↔SCH | `iwxxm-validate` + convert validate hooks |

**No** new apps/; **no** HTTP YAML fields; **no** new third-party deps expected.

## Connectivity

**H4–H5 N/A** unless Build changes OpenAPI/UI (D-YFC-07).

## Milestones → tasks (Build after gate)

| M | Issue | Sketch |
|---|-------|--------|
| M1 | #1227 | Starter templates; cookbook; `--check-overlay`; README smoke; TC-EVYFC-003 |
| M2 | #1228 | METAR+SPECI packs/policies/detectors/IWXXM/pack-IR → full; goldens |
| M3 | #1229 | Accept ADR-047; emit map METAR→SPECI; TC-EVYFC-002 |
| M4 | #1230 | TAF/SIGMET/AIRMET/VAA/TCA parallel PRs to full |
| M5 | #1231 | Matrix all-full + pin↔SCH; TC-EVYFC-001/004 |

## Decisions (tech)

| ID | Choice |
|----|--------|
| TP-YFC-01 | Declarative emit map over plugins (ADR-047) |
| TP-YFC-02 | Stable `convert` API |
| TP-YFC-03 | Multi-PR parallel products in M4 |
| TP-YFC-04 | No new deps without AskQuestion |
| TP-YFC-05 | H4–H5 waived unless UI/OpenAPI |
| TP-YFC-06 | Scale **full** verify angles at documenting/implementing gates |

## Branch / PR

- Spec docs: `evolve/EV-yaml-full-configurability` → `--base stage`
- Build: milestone branches from `stage` after gate open
