# Routing plan — S069 / EV-059

**Status:** **completed** (`D-S069-close=1`; promote held)  
**Preset:** **Lean** (CI/DX tooling; full entry interview completed)  
**PR target:** `stage` (two PRs; promote held)  
**Branch:** `evolve/EV-059-ci-schemathesis-mutation` @ `stage@c458669e` → tip `8755ae87`  
**UI preview:** **N/A** (`D-S069-e6`)  
**Spec→Build gate:** **open** (Build band complete)

## Spec-development band

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Open S069; board In progress; Lean routing approved |
| 16-evolve | yes | orchestrate | **completed** | EV-059 closed `D-S069-close=1` |
| 01-requirements | yes | delta | **completed** | `D-S069-01-ac=2b`; F34 + TC-F34-001..007; report `reports/01-requirements.md` |
| 02-verify-plan | yes | delta | **completed** | Gate A **PASS** (`D-S069-gateA=1a`); report `reports/02-verify-plan.md` |
| 03-plan-tooling | no | — | skipped | No new Cursor rules expected |
| 04-tech-plan | no | — | skipped | Lean — tickets + ACs sufficient |
| 05-verify-tech | no | — | skipped | Lean |
| 06-tech-tooling | no | — | skipped | Deps via inventory AskQuestion in 01/07 |

## Build band

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 07-build | yes | delta | **completed** | M1 #997 + M2 #998 MERGED → `stage` @ `8755ae87` |
| 08-verify-build | yes | delta | **completed** | Lean PASS — `reports/verification-report.md`; CI `32054972352` SUCCESS |
| 09-qa | no | — | skipped | Lean |
| 10-e2e | no | — | skipped | No UI / H4–H5 |
| 11-verify-impl | no | — | skipped | Lean |
| 12-verify-deploy | no | — | skipped | No deploy |
| 13-deploy-smoke | no | — | skipped | No staging smoke this cycle |

## Recommended ordered stages

`00 → 16 → 01 → 02` → ★ Spec→Build **open** → `07 → 08` — **complete**

## Skip rationale

- **Lean Spec:** tickets #727/#874 + epic #841 already specify AC; product/tests/tech-spec/api deltas only.
- **Build 07→08:** implement suites + fix findings; verify locally/CI.
- **Skip 09–13:** no operator UI, no deploy/promote; connectivity H4–H5 N/A.
- **CI cost:** Schemathesis path-filtered required; mutation nightly/manual only (`D-S069-ci`).

## Board / velocity

- #727, #874, #841 **CLOSED** / Done
- Two PRs landed separately (#997 then #998)
