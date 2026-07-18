# T3.6 — xsdata codegen pipeline + CI hook (ADR-027 / E10-40)

**Session:** S014 / EV-010  
**Task:** T3.6  
**Date:** 2026-07-18

## Deliverables

| Item           | Path                                                                          |
| -------------- | ----------------------------------------------------------------------------- |
| Pipeline       | `scripts/codegen/iwxxm_xsd.py`                                                |
| Makefile       | `make codegen-iwxxm-xsd`                                                      |
| Output package | `packages/shared/src/metar_shared/iwxxm_xsd/`                                 |
| CI hook        | `.github/workflows/vendor-sync.yml` → `make codegen-iwxxm-xsd` after pin sync |
| Tests          | `tests/codegen/test_iwxxm_xsd_pipeline.py`                                    |

## Behaviour

- Entry XSD: `vendor/schemas/iwxxm/{version}/IWXXM/iwxxm.xsd` (override with `--entry`)
- Output format: **pydantic** via xsdata-pydantic
- Soft-handles known GML quirks: duplicate `Field(default=…)` (ruff) and circular imports
- Generated `v*` trees gitignored until T3.7 commits models; skeleton + README tracked

## Next

- **T3.7a** — regen smoke: importable / non-empty models
- **T3.7** — commit/regenerate models; msgspec/Rust adapt follow-on
