# 04-tech-plan — S059 / EV-050

**Mode:** delta / Standard  
**Date:** 2026-08-09  
**Corpus:** [Corpus: product] [Corpus: tests] [Corpus: tech-spec] [Corpus: decisions]

## Locked tech decisions

| ID | Choice |
|----|--------|
| D-S059-04-milestones | **1** — M1 harvest · M2 membership+fixtures · M3 profiles · M4 closeout |
| D-S059-04-harvest | **1** — CSV `notation` + pin RDF for nil/dual |
| D-S059-04-wire | **1** — Generated artifact in `tac-validate` + pytest + make regen |
| D-S059-04-adr | **1** — No new ADR |

## Artifacts

| Path | Role |
|------|------|
| `reports/execution-plan.md` | Phases / milestones / T1.1–T4.3 |
| `build-plan-card.md` | Active M1 batch (T1.1–T1.4) |

## Stack / connectivity

- Existing uv/Python monorepo; extend offline harvest pattern from `tac2iwxxm.codelists`
- No new runtime deps (06 skipped)
- H4–H5 / CORS / staging secrets: **N/A** (no browser UI)

## Exit

- [x] Tech interview locked (user `1,1,1,1`)
- [x] Execution plan + Build Plan Card drafted
- [x] User approve plan (`D-S059-04-plan=1`) → **05-verify-tech**
