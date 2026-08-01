# Evolve summary — S034 / EV-027

**Title**: #815 official WMO decode residual matrix  
**Preset**: Lean+build (+13 when ships → **waived**)  
**Features deepened**: F25 / F9 / F7.g — no new Fn  
**Issues**: #815 **closed**; child #820 **open** (VAA/TCA G4)  
**Branch**: `evolve/EV-027-wmo-decode-residual-matrix`  
**PR**: [#821](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/821) **merged** `ad36aa0`  
**Deploy smoke**: waived (`D-S034-gate-c` / TC-EV027-005)  
**Merge decision**: `D-S034-merge` — 1,1 (merge at green tip; leave local tip for closeout)

## Outcomes

- Inventory of official WMO TAC peers (vendor pin + mirrored annex3) locked to catalog ∪ `FIXTURE_GAPS`
- Parametrized residual matrix CI: happy-path peers → empty or allowlisted residuals
- Decode fixes in-cycle where cheap; VAA/TCA G4 allowlist + child #820
- 08-verify-build + 10-e2e smoke PASS; Gate C PASS; GitHub #815 closed

## Artifacts

- `reports/execution-plan.md`, `t0-1-inventory-dig.md`
- `reports/01-requirements.md`, `02-verify-plan-audit.md`, `04-tech-plan.md`
- `reports/verification-report.md`, `e2e-report.md`
- Corpus deltas: feature-list / UJ-042 / test-plan / decisions
- Standing report: `docs/evolve-report-EV-027.md`
- Intake context: `docs/context/wmo-decode-residual-matrix.md`

## Follow-ups

[#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) — VAA/TCA residual deepen beyond F9 G4.
