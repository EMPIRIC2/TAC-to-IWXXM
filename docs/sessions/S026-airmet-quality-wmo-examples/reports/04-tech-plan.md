# 04-tech-plan — S026 / EV-020

**Started**: 2026-07-29  
**Completed**: 2026-07-29  
**Mode**: evolve delta  
**Features**: F24, F25 + deepen F9 / F7.g / F6 / F3  
**Branch**: `evolve/EV-020-airmet-quality`  
**Status**: **completed** — plan approved E20-F8=1; handoff 07 @ T0.1

## Toolchain baseline (detected)

| Area | Choice |
|------|--------|
| Template | `static+api+worker` |
| Packages | `tac2iwxxm`, `tac-validate`, `iwxxm-validate`; FE Vite |
| Registry | ADR-028 reuse (AIRMET rows) |
| Golden compare | `canonicalize_xml` under defaults (ADR-032 Accepted) |
| Glossary | Official sources + `decode_glossary.yaml`; env `TAC2IWXXM_DECODE_GLOSSARY_PATH` |
| Deploy | Existing Render API+FE; H4–H5 when FE |
| New deps | Prefer none; PyYAML allowed (E20-F5=2) |

## Milestone order (approved)

| M | Focus |
|---|--------|
| M0 | Research + combined `wmo-quality.yml` |
| M1 | F24 AIRMET lint A1–A2 |
| M2 | F24 AIRMET golden A3 (+ A4) |
| M3 | F25 METAR/SPECI W1–W2 |
| M4 | F25 TAF W3 |
| M5 | F9 glossary + F7.g/W4 catalog |
| M6 | Smoke / 08 / 10 / 11 / 13 |

## Interview locks

| ID | Decision |
|----|----------|
| E20-F1 | Milestone order **1** |
| E20-F2 | Research **1** — full mining |
| E20-F3 | CI **3** — `wmo-quality.yml` |
| E20-F4 | FE unlock **1** — incremental |
| E20-F5 | Deps **2** — PyYAML if needed |
| E20-F6 | Deploy **1** — H4–H5 required |
| E20-F7 | Kill-switch **1** |
| E20-F8 | Plan **1** — approve → 07 @ T0.1 |

## Artifacts

- `reports/execution-plan.md` — **approved**
- 04-exit consistency — **PASS** (05 skipped)

## Next

**07-build** — T0.1 research catalog.
