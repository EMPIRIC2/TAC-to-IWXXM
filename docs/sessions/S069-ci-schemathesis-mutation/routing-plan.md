# Routing plan — S069 / EV-059

**Status:** **approved** (`D-S069-route=1a/2a/3a/4a`; Spec→Build **open** `D-S069-spec-build=2a`)  
**Preset:** **Lean** (CI/DX tooling; full entry interview completed)  
**PR target:** `stage` (two PRs; promote held)  
**Branch:** `evolve/EV-059-ci-schemathesis-mutation` @ `stage@c458669e`  
**UI preview:** **N/A** (`D-S069-e6`)  
**Spec→Build gate:** **open** (`D-S069-gateA=1a`, `D-S069-spec-build=2a`)

## Spec-development band

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Open S069; board In progress; Lean routing approved |
| 16-evolve | yes | orchestrate | **in_progress** | EV-059; Build phase; next child 07-build |
| 01-requirements | yes | delta | **completed** | `D-S069-01-ac=2b`; F34 + TC-F34-001..007; report `reports/01-requirements.md` |
| 02-verify-plan | yes | delta | **completed** | Gate A **PASS** (`D-S069-gateA=1a`); report `reports/02-verify-plan.md` |
| 03-plan-tooling | no | — | skipped | No new Cursor rules expected |
| 04-tech-plan | no | — | skipped | Lean — tickets + ACs sufficient |
| 05-verify-tech | no | — | skipped | Lean |
| 06-tech-tooling | no | — | skipped | Deps via inventory AskQuestion in 01/07 |

## Build band (unblocked)

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 07-build | yes | delta | **in_progress** | M1 #997 merged; M2 PR [#998](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/998) open (`Closes #874`) |
| 08-verify-build | yes | delta | **completed** | Lean M2 PASS — `reports/verification-report.md`; CI comment jobs waived (`D-S069-ci-comment-waiver`) |
| 09-qa | no | — | skipped | Lean |
| 10-e2e | no | — | skipped | No UI / H4–H5 |
| 11-verify-impl | no | — | skipped | Lean |
| 12-verify-deploy | no | — | skipped | No deploy |
| 13-deploy-smoke | no | — | skipped | No staging smoke this cycle |

## Recommended ordered stages

`00 → 16 → 01 → 02` → ★ Spec→Build **open** → `07 → 08`

## Skip rationale

- **Lean Spec:** tickets #727/#874 + epic #841 already specify AC; product/tests/tech-spec/api deltas only.
- **Build 07→08:** implement suites + fix findings; verify locally/CI.
- **Skip 09–13:** no operator UI, no deploy/promote; connectivity H4–H5 N/A.
- **CI cost:** Schemathesis path-filtered required; mutation nightly/manual only (`D-S069-ci`).

## Board / velocity

- WIP: #841, #727, #874 **In progress**
- Do not bundle #727 + #874 into one PR

## Locked decisions

| ID | Decision |
|----|----------|
| D-S069-e0 … D-S069-e8 | See session-brief |
| D-S069-ci | Schemathesis path-filtered required; mutation nightly/manual |
| D-S069-tool | pytest-gremlins + Stryker |
| D-S069-fn | Allocate **F34** |
| D-S069-gateA | **1a** — PASS |
| D-S069-spec-build | **2a** — Open Build (07→08) |
