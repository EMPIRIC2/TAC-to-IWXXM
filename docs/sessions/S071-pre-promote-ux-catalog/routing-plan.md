# Routing plan — S071 / EV-061

**Status:** **approved** (`D-S071-e9` — Spec-development only)  
**Preset:** **Standard**  
**PR target:** `stage` (promote held until #1015)  
**Branch:** `evolve/EV-061-pre-promote-ux-catalog` @ `stage@a1650b01`  
**UI preview:** **Remind at 11-verify-impl** (`D-S071-e2`)  
**Spec→Build gate:** **closed**

## Spec-development band

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Open S071/EV-061; EV0–EV9 locked |
| 16-evolve | yes | orchestrate | **in_progress** | Spec→Build **closed**; 04 drafted; dual Spec next after plan approve |
| 01-requirements | yes | delta | **completed** | Deepen F7/F2/F6/F9/F10/F15/F34; UJs for catalog/AHL/bars/validate |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS `D-S071-gateA=1a` |
| 03-plan-tooling | no | — | skipped | Unless 04 finds Cursor rules |
| 04-tech-plan | yes | delta | **in_progress** | Execution plan M1–M6; TC stubs; api delta; pending `D-S071-04-plan` |
| 05-verify-tech | no | — | skipped | Unless 04 finds deps |
| 06-tech-tooling | no | — | skipped | CI gate may be workflow-only under 04/07 |
| uat (Spec) | yes | dual Spec | pending | Catalog + AHL + validate UX + bars |
| verify-qa (Spec) | yes | dual Spec | pending | TC matrix for #1010–#1015 |

## Build band (`blocked_until_spec_gate`)

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 07-build | yes | delta | blocked_until_spec_gate | After Spec→Build open |
| 08-verify-build | yes | delta | blocked_until_spec_gate | |
| 09-qa | yes | delta | blocked_until_spec_gate | |
| 10-e2e | yes | delta | blocked_until_spec_gate | Catalog tab + AHL + bars |
| 11-verify-impl | yes | delta | blocked_until_spec_gate | Non-deployed UI preview |
| 12-verify-deploy | yes | delta | blocked_until_spec_gate | |
| 13-deploy-smoke | yes | delta | blocked_until_spec_gate | staging; promote held until #1015 |
| uat (Build) | yes | dual Build | blocked_until_spec_gate | |

## Spec → Build gate

- **status:** `closed`
- **rule:** No product implementation / 07+ until AskQuestion opens or waives gate

## Recommended ordered stages

`00 → 16 → 01 → 02 → 04` (+ uat Spec / verify-qa Spec) → ★ Spec→Build AskQuestion → `07 → 08 → 09 → 10 → 11 → 12 → 13`

## Skip rationale

- **Standard Spec:** multi-surface UI + API + CI needs 01/02 + 04.
- **Skip 03/05/06** unless 04 finds rules/deps; CI hardening can live in 04 EP + 07.
- **Build Standard** with H4–H5 when UI ships; dual uat.

## Board / velocity

- Epic #1009 on **M0**
- Children #1010–#1015 Ready / In progress per board WIP ≤2 during Build
- Related OOS: #996, #840, #837

## Locked intake decisions

See [session-brief.md](session-brief.md) and [evolve-decisions.md](../../decisions/evolve-decisions.md) §Cycle EV-061.
