# Scoped context: Canonical MET + staged validation (#925)

> **Status**: active  
> **Created**: 2026-09-03  
> **Session**: `EV-925-canonical-met-staged-validation`  
> **Tickets**: [#925](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/925) · [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)  
> **Corpus**: [Corpus: product] F2/F6/F15 · [Corpus: adr] ADR-036, ADR-039

## Goal

Investigate canonical MET IR + staged validation pipeline. Map stages to current packages. Recommend keep-in-place vs `packages/core/canonical-model`. No production ship.

## Recommendation (draft)

Keep IR in `tac2iwxxm` (`ConvertResult.ir`); accept ADR-039 PipelineResult contract; extend `StageResult` platform-wide later.

## Key code paths

| Concern | Location |
|---------|----------|
| IR dict | `packages/tac2iwxxm/models.py` `ConvertResult.ir` |
| Product parse | `packages/tac2iwxxm/products/*.py` |
| TAC lint | `packages/tac-validate` → `LintReport` |
| IWXXM staged | `packages/iwxxm-validate/ca_eccc_validate.py` → `StageResult` |
| HTTP validate | `apps/backend/routers/comprehensive_validation.py` |

## Out of scope

#931 workflows · #938 inspector · typed IR msgspec · package extract
