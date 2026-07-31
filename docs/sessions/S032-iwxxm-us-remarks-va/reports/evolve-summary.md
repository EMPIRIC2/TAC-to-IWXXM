# Evolve summary — S032 / EV-025

**Title**: iwxxm-us REMARKS encode (full dig ❌) + VA multi-location golden  
**Preset**: Lean+build (+13 when ships)  
**Features deepened**: F6 / F6.b / F12 / F2 / F13 / F23 — no new Fn  
**Issues**: #810 / #811 / #812 / #809  
**Branch**: `evolve/EV-025-iwxxm-us-remarks-va`  
**PR**: [#816](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/816) open — close EV-025 after merge (`D-S032-EV025-closeout=1`)  
**Close decision**: Defer T7.3 / 13-deploy-smoke until API convert/validate ships; open PR to main

## Outcomes

- Lane A: encode all dig ❌ iwxxm-us REMARKS types (#810 Variable RVR, #811 Lightning/VOP, #812 SnowIncrease + sensors, adjacent dig packs)
- Lane B: #809 `sigmet-multi-location-VA` soft-compare golden; catalog stays `wmoReference` until ADR-032 equality
- US fixtures stay out of WMO sample menu; combined-catalog validate smoke green
- Gate C dig encode PASS; 08-verify-build + 10-e2e smoke PASS (T7.2 @ `1e46b38`)

## Artifacts

- `reports/execution-plan.md`, `us-remarks-va-theme-map.md`, `dig-checklist-code-audit.md`
- `reports/t7-1-gate-c-dig-close.md`, `verification-report.md`, `e2e-report.md`
- Corpus deltas: feature-list, user-journeys, test-plan, spec

## Follow-ups

- **T7.3 / 13-deploy-smoke** when convert/validate behavior ships on Render
- ADR-032 equality / `wmoPass` promote for `sigmet-multi-location-VA` (TC-EV025-009)
