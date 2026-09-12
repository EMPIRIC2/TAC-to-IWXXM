# 12-verify-deploy — S067 / EV-057

> Generated: 2026-08-16 (updated)  
> **env_role**: staging (PR → `stage`); prod apex #948 already live  
> Tip: `d05c23b7` · CI [31965556483](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31965556483) **success**  
> Corpus: [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: product §F7] [Corpus: product §F30]

## Target

| Item | Value |
|------|--------|
| PR | https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/991 |
| Base | `stage` |
| Head | `evolve/EV-057-m0-ready-apex-accumulate-validate` @ `d05c23b7` |
| Staging cluster | `metar-iwxxm-staging` / `app.staging.tac-to-iwxxm.com` |
| Promote | **held** (`D-S067-promote=2b`) |

## Decisions

| ID | Value |
|----|--------|
| D-S067-12-resume | **1a** — finish checklist for tip `d05c23b7` / PR #991 |
| D-S067-12-scope | **1a** — no delta; #948/#903/#838 → stage; promote held |
| D-S067-12-risks | **1a** — approve standard stage mitigations |
| D-S067-12-merge | **1a** — approve rollback + checklist → merge #991 → stage → 13 |

## Connectivity (ready for 13)

| Row | Status |
|-----|--------|
| H0c | PASS (08/09) |
| CORS origins | existing `app` / `app.staging` — no new convert CORS |
| `verify_connectivity.sh` | present |
| H4–H5 | **13** after staging CD |

## Outcome

| Step | Result |
|------|--------|
| Checklist | **APPROVED** (`D-S067-12-*` recommended) |
| Merge | [#991](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/991) → `stage` @ `d7022f1f` |
| CI/CD | [31966102210](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31966102210) **success** |
| Deploy (stage) | **success** |
| Staging smoke | **success** |
| Board | #948 / #903 / #838 → **On stage** |
| Promote | **held** (`D-S067-promote=2b`) |

**12-verify-deploy COMPLETE.** Next: **13-deploy-smoke** (startup interview).
