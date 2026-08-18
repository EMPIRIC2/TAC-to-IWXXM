# Routing plan — S070 / EV-060

**Status:** **approved** (`D-S070-e9` recommended — Spec-development only)  
**Preset:** **Standard**  
**PR target:** `stage` (promote held — `D-S070-e5`)  
**Branch:** `evolve/EV-060-converter-operator-bugs` @ `stage@8755ae87`  
**UI preview:** **Remind at 11-verify-impl** (`D-S070-e2`)  
**Spec→Build gate:** **open** (`D-S070-spec-build=1a`)  
**Issue order (Build PRs):** #1001 → #1003 → (#1002+#1004+#1005) → #1006

## Spec-development band

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Open S070/EV-060; EV0–EV9 locked recommended |
| 16-evolve | yes | orchestrate | **in_progress** | Spec→Build **open**; 07 M1 #1001 |
| 01-requirements | yes | delta | **completed** | F7.t + F6/F2/F10/F29/F31; UJ-059..063; api product=iwxxm; report `reports/01-requirements.md` |
| 02-verify-plan | yes | delta | **completed** | Gate A **PASS** (`D-S070-gateA=1a`); report `reports/02-verify-plan.md` |
| 03-plan-tooling | no | — | skipped | No new Cursor rules expected |
| 04-tech-plan | yes | delta | **completed** | EP approved `D-S070-04-plan=1a`; M1–M4 four PRs |
| 05-verify-tech | no | — | skipped | Unless 04 finds deps |
| 06-tech-tooling | no | — | skipped | No new deps expected |
| uat (Spec) | yes | dual Spec | **completed** | `uat-script.md` Auth + converter AC |
| verify-qa (Spec) | yes | dual Spec | **completed** | `reports/verify-qa-spec.md` |

## Build band (blocked until Spec→Build gate)

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 07-build | yes | delta | **in_progress** | M1 #1001 AHL first (`D-S070-spec-build=1a`) |
| 08-verify-build | yes | delta | blocked_until_spec_gate | After each milestone / before C→D |
| 09-qa | yes | delta | blocked_until_spec_gate | Converter + Auth |
| 10-e2e | yes | delta | blocked_until_spec_gate | Playwright AHL, product=IWXXM, profile a11y, bulletin fields, Auth |
| 11-verify-impl | yes | delta | blocked_until_spec_gate | Per-Fn AC; UI preview offer |
| 12-verify-deploy | yes | delta | blocked_until_spec_gate | Staging |
| 13-deploy-smoke | yes | delta | blocked_until_spec_gate | `env_role: staging`; promote held |
| uat (Build) | yes | dual Build | blocked_until_spec_gate | Facilitated Auth + converter UAT |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 04` (+ uat Spec / verify-qa Spec) → ★ Spec→Build **open** → `07 → 08 → 09 → 10 → 11 → 12 → 13`

## Skip rationale

- **Standard Spec:** API + UI + package behavior needs 01/02 plus 04 execution plan (`D-S070-e4`).
- **Skip 03/05/06** unless 04 finds new deps or Cursor rules.
- **Build Standard:** 07–13 + dual uat; H4–H5 when UI ships.
- **Promote:** not automatic after 13 — re-approve after staging smoke.

## Board / velocity

- Epic #1000 **Backlog** (do not In progress)
- Children #1001–#1006 **Ready** (WIP 0 until 07; then ≤2 In progress)
- Later profile view/create: #933 / #924 (not this cycle)

## Locked intake decisions

See [session-brief.md](session-brief.md) table and [evolve-decisions.md](../../decisions/evolve-decisions.md) §EV-060.
