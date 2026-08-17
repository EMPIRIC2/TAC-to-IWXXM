# Routing plan — S068 / EV-058

**Status:** **approved** (`D-S068-route=1a/2a/3a`)  
**Preset:** **Lean** (user-approved; pure UI / small blast radius — not Auto-Lean skip of intake)  
**PR target:** `stage`  
**Branch:** `evolve/EV-058-quality-metrics-diff-layout` @ `stage@c2ca9a3f`  
**UI preview:** **Yes** — non-deployed local (`D-S068-ui-preview=1`) → http://127.0.0.1:18000/  
**Spec→Build gate:** **open** (`D-S068-spec-build=1a`)
**Gate A:** **PASS** (`D-S068-gateA=1`)

## Spec-development band

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Open S068; #983 In progress; Lean routing approved |
| 16-evolve | yes | orchestrate | **in_progress** | Build open; FE implement → 10 → 13 |
| 01-requirements | yes | delta | **completed** | `D-S068-01-ac=2b`; AC1–AC5; UJ-056 + TC-EV058 |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS `D-S068-gateA=1` |
| 03-plan-tooling | no | — | skipped | No new Cursor rules expected |
| 04-tech-plan | no | — | skipped | Lean — FE layout toggle only |
| 05-verify-tech | no | — | skipped | Lean |
| 06-tech-tooling | no | — | skipped | No new deps unless AskQuestion |

## Build band

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 07-build | no | — | skipped | Lean: 16 Agent implements after Gate A |
| 08-verify-build | no | — | skipped | Lean |
| 09-qa | no | — | skipped | Lean |
| 10-e2e | yes | delta | **completed** | UJ-056 4/4 PASS local; H4–H5 via 13 |
| 11-verify-impl | no | — | skipped | Lean |
| 12-verify-deploy | no | — | skipped | Lean (PR path via 13) |
| 13-deploy-smoke | yes | delta | pending | Stage smoke after merge |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 10 → 13`

## Skip rationale

- **Lean (user):** FE-only layout choice on existing `/quality/:stem`; C14N unchanged; reuse `unifiedLineDiff`.
- **Skip 03/04/05/06/07/08/09/11/12:** no new guardrails/stack/Standard milestones; 16 orchestrates implementation after 01/02 Gate A.
- **Include 10 + 13:** operator UI + staging H4–H5 / smoke for UJ-056 layout modes.

## Board / velocity

- WIP: #983 **In progress** (1 ≤ 2)
- Ready: refill after this pull as needed (3–5 target)

## Locked / pending decisions

| ID | Decision |
|----|----------|
| D-S068-e0 | **1a/2b/3a/4a/5a** — goal/scope/success/constraints/proceed |
| D-S068-e1e2 | **recommended** — feature; #983; operator; F7.q+UJ-056 |
| D-S068-e3e4 | **1a–4a** — docs; no CORPUS gap; Lean Spec; FE Build intent |
| D-S068-e5e6 | **1a–4a** — out-of-scope fence; H4–H5; local preview |
| D-S068-route | **1a/2a/3a** — Lean bands; Spec→Build closed; open Spec |
| D-S068-ui-preview | **1** — http://127.0.0.1:18000/ |
| D-S068-board | **1** — #983 → In progress |
| D-S068-01-ac | **2b** — AC1–AC5; synced scroll best-effort |
| D-S068-01-control | **3a** — segmented Inline \| Side-by-side |
| D-S068-01-uj | **4a** — deepen UJ-056 + TC-EV058-001..005 |
