# Routing plan — S067 / EV-057

**Status:** **approved** (`D-S067-proceed=4a` / `D-S067-preset=4a`)  
**Preset:** **Standard**  
**PR target:** `stage` (promote to `main` only after separate re-approve — `D-S067-promote=2b`)  
**Branch:** `evolve/EV-057-m0-ready-apex-accumulate-validate` @ `stage@b796882e`  
**UI preview:** **Remind at 11-verify-impl** (`D-S067-ui-preview=3a`)  
**Issue order:** #948 → #903 → #838

## Stages

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Open S067/EV-057; #948 In progress; interview locked |
| 16-evolve | yes | orchestrate | **in_progress** | Plan card + Phase 0–1 → child stages |
| 01-requirements | yes | delta | **completed** | AC locked `D-S067-01-ac=1`; F7.r/F7.s/F30; UJ-057/058/OPS-002 |
| 02-verify-plan | yes | delta | **completed** | Gate A **PASS** `D-S067-gateA=1`; cap≤200; FE Ingress redirect |
| 03-plan-tooling | no | — | skipped | No new Cursor rules expected unless AskQuestion |
| 04-tech-plan | yes | delta | **completed** | EP approved `D-S067-04-plan=1`; sibling apex Ingress |
| 05-verify-tech | no | — | skipped | Per `D-S067-04-next=1a` |
| 06-tech-tooling | no | — | skipped | No new deps |
| 07-build | yes | delta | **completed** | M1 live #948 AC met; M2/M3 repo done (`D-S067-948-apply=1a`) |
| 08-verify-build | yes | delta | **completed** | PASS 2026-08-16; live UJ-OPS-002 green |
| 09-qa | yes | delta | **pending** | Parallel with 10 |
| 10-e2e | yes | delta | **pending** | UJ-057/UJ-058 Playwright; UJ-OPS-002 live curl done |
| 11-verify-impl | yes | delta | **pending** | Per-Fn AC + UI preview remind |
| 12-verify-deploy | yes | delta | **pending** | PR → stage; release prep only if promote later |
| 13-deploy-smoke | yes | delta | **pending** | Staging H0c–H5; then promote AskQuestion |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 04 → 07 → 08 → 09 → 10 → 11 → 12 → 13`

## Skip rationale

- **Standard (user `D-S067-preset=4a`):** multi-issue pack with UI + infra + stage/smoke; not Auto-Lean.
- **Skip 03/05/06** unless Gate A/B or deps force them back in via AskQuestion.
- **Promote:** not automatic after 13 — `D-S067-promote=2b` requires re-approve after all three are on `stage`.

## Board / velocity

- WIP: #948 **In progress** (1 ≤ 2)
- Ready: #903, #838 (held until their milestones)
- Out: #841 Backlog

## Locked intake decisions

| ID | Decision |
|----|----------|
| D-S067-first | **1a** — #948 first |
| D-S067-pack | **2c** — one cycle all three |
| D-S067-success | **3c** — stage + promote path |
| D-S067-oos | **1a** — defaults |
| D-S067-promote | **2b** — stage all three; promote after re-approve |
| D-S067-blockers | **3a** — none known |
| D-S067-preset | **4a** — Standard |
| D-S067-type | **1a** — feature / 16-evolve |
| D-S067-order | **2a** — #948 → #903 → #838 |
| D-S067-ui-preview | **3a** — remind at 11 |
| D-S067-proceed | **4a** — open session |
| D-S067-board | **1** — #948 In progress |
