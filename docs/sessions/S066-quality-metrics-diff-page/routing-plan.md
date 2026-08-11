# Routing plan — S066 / EV-056

**Status:** **approved** (`D-S066-route=1`)  
**Preset:** **Lean** (user-requested; not Auto-Lean — dedicated route + UJ-056 deepen)  
**PR target:** `stage`  
**Branch:** `evolve/EV-056-quality-metrics-diff-page` @ `stage@340b3cf6`  
**UI preview:** **Yes** — non-deployed local (`D-S066-ui-preview=1`) → http://127.0.0.1:18000/

## Stages

| Stage | Include? | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | **completed** | Close S065; open S066; #988 In progress; `D-S066-route=1` / `D-S066-ui-preview=1` |
| 16-evolve | yes | orchestrate | **in_progress** | Plan card + Phase 0–1 → child stages |
| 01-requirements | yes | delta | pending | F7.q AC + UJ-056 deepen; no new Fn |
| 02-verify-plan | yes | delta | pending | Gate A |
| 03-plan-tooling | no | — | skipped | No new Cursor rules expected |
| 04-tech-plan | no | — | skipped | Lean — FE route + hunk fold; no API/arch |
| 05-verify-tech | no | — | skipped | Lean |
| 06-tech-tooling | no | — | skipped | No new deps unless AskQuestion |
| 07-build | no | — | skipped | Implementation via 16 Agent after Gate A (Lean) |
| 08-verify-build | no | — | skipped | Lean |
| 09-qa | no | — | skipped | Lean |
| 10-e2e | yes | delta | pending | UJ-056 / Playwright deepen |
| 11-verify-impl | no | — | skipped | Lean |
| 12-verify-deploy | no | — | skipped | Lean — merge path via 13 |
| 13-deploy-smoke | yes | delta | pending | Staging smoke after PR → stage |

## Recommended ordered stages

`00 → 16 → 01 → 02 → 10 → 13`

## Skip rationale

- **Lean (user):** UX/docs/tests deepen on existing Quality metrics; C14N semantics unchanged; API only if routing needs a path (prefer FE shell route).
- **Skip 03/04/05/06/07/08/09/11/12:** no new guardrails, stack, or Standard build milestones; 16 orchestrates Agent implementation after 01/02 Gate A.
- **Include 10 + 13:** operator UI + staging H4–H5 / smoke for UJ-056.

## Board / velocity

- WIP: #988 **In progress** (1 ≤ 2)
- Ready: 4 shippable (#948, #958, #981, #983) — within 3–5

## Locked / pending decisions

| ID | Decision |
|----|----------|
| D-S065-close | **1** — merge #987; close S065; open S066 |
| D-S066-board | **1** — #988 → In progress |
| D-S066-route | **1** — Lean as drafted (`00 → 16 → 01 → 02 → 10 → 13`) |
| D-S066-ui-preview | **1** — non-deployed local UI at http://127.0.0.1:18000/ |
