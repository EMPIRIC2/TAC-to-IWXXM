# 04-tech-plan — S040 / EV-032

**Started**: 2026-08-04  
**Completed**: 2026-08-04 (pending Gate B)  
**Mode**: evolve delta  
**Features**: **F32** + deepen F23 (#835) / F4 / F6 / F2 / F13 (#808 + corpus)  
**Branch**: `evolve/EV-032-iwxxm-corpus-quality`  
**Status**: **awaiting Gate B** (`D-S040-04-plan`)

## Toolchain baseline

| Area | Choice |
|------|--------|
| Template | `static+api+worker` |
| #835 | Strict ADR-032 → `wmoPass` |
| F32 | Cookbook + fixtures; `annex3_products` peer VAA/SWXA; AHL in M2 |
| New deps | None |
| Deploy | API + static; H1–H3; **H4–H5 required** |
| Local CI | Path-filtered **pre-commit** smokes; long packs **pre-push** / `make test-*-quality` |
| Docs | Session inventory + `docs/domain/iwxxm/` for #808/#847 |

## Interview locks

| Batch | Decision |
|-------|----------|
| Batch 1 `1,1,1,1` | M0–M4; strict ADR-032; cookbook+fixtures; AHL discover M2 |
| Batch 2 `1,1,custom,1` | No new deps; H4–H5 required; tiered local CI (E32-T7); session+domain docs |
| Gate B | awaiting |

## Artifacts

- `reports/execution-plan.md` — **draft** (28 tasks, M0–M4)
- This report — pending Gate B

## Next

Approve Gate B → **07-build @ T0.1**.
