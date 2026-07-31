# Evolve summary — S033 / EV-026

**Title**: #809 VA multi-location ADR-032 equality + catalog wmoPass  
**Preset**: Lean+build (+13 when ships)  
**Features deepened**: F23 / F6 / F7 — no new Fn  
**Issues**: #809 **closed**  
**Branch**: `evolve/EV-026-va-multi-location-equality`  
**PR**: [#817](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/817) **merged** `101f555`  
**Deploy smoke**: [#818](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/818) closeout docs; live PASS (`D-S033-13-smoke-pass`)  
**Close decision**: `D-S033-EV026-phase4-close` — approve 13 results + close cycle/session

## Outcomes

- Encoder deltas for WMO `sigmet-multi-location-VA` so `canonicalize_xml` equals vendor under annex3 defaults (calendar/ATS–MWO stamps, ring order + 2dp coords, phenomenonTime xlink reuse)
- TC-EV025-008 strict equality green; catalog `sigmet_multi_location_va` → `wmoPass` (TC-EV025-009 / Vitest)
- FIXTURE_GAPS cleared for equality-pending note; Gate C PASS; GitHub #809 closed
- 08-verify-build + 10-e2e smoke PASS; T3.4 / 13-deploy-smoke PASS on Render after #817

## Artifacts

- `reports/execution-plan.md`, `t0-1-canonicalize-diff-themes.md`, `t3-1-gate-c-dig.md`
- `reports/01-requirements.md`, `02-verify-plan-audit.md`, `04-tech-plan.md`
- `reports/verification-report.md`, `deploy-smoke.md`
- Corpus deltas: feature-list / UJ-041 / test-plan / FIXTURE_GAPS / decisions
- Standing report: `docs/evolve-report-EV-026.md`
- Intake context: `docs/context/va-multi-location-809.md`

## Follow-ups

None blocking for #809. Optional: deepen other SIGMET family stems under F23 as separate cycles.
