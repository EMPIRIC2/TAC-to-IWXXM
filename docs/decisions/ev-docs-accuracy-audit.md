# EV-docs-accuracy-audit — decisions

**Session:** EV-docs-accuracy-audit  
**Date:** 2026-09-12  
**Orchestrator:** evolve  

## Intake / requirements (accepted defaults)

| ID | Decision |
|----|----------|
| R1 | Prod `/auth/register` OpenAPI omission → **deploy lag, not code bug**. Staging: route present (422 on `{}`). Prod: **404** / OpenAPI omit. Code on `main` (#1180/#1183) always mounts register (`test_auth_router_mount_unit`). Last prod tag `v2026.09.10-deploy` predates ship. **Ops:** cut `vYYYY.MM.DD-deploy` on `main` tip when ready to roll prod ([Corpus: deploy]). |
| R2 | F7 feature-list status → **Implemented** (remaining work tracked as open issues, not umbrella Planned). |
| R3 | GIFTs-era `guides/API.md` + `ARCHITECTURE.md` → **obsolete banner + not design-gate** (CORPUS already opt-in). |
| R4 | Build/doc patch scope → **P0+P1** from `AUDIT-ROLLUP.md` only (no full test-plan slim). |
| R5 | After documenting verify → **AskQuestion to open Build** for register investigation + any remaining code. |

## Doc deltas this Spec band

- Scrub or retarget dead `docs/context/` / missing `reports/e2e-report` cites on audited spine files
- Align F5 detail status with summary; F7 → Implemented
- ADR index: ADR-020 Superseded; ADR-011/012 Historical
- `spec.md` repository tree refresh; `config-spec` DOKS `/config.json` example
- `api-contract`: register skew note; drop ghost `/auth/health`; thin OpenAPI pointers for eval/validation/schema-status; demote Render base URL
- `test-plan` H7 row; `NOW.md` session pointer
- Guide banners on GIFTs-era API/ARCHITECTURE

[Corpus: product] [Corpus: api] [Corpus: adr] [Corpus: decisions]
