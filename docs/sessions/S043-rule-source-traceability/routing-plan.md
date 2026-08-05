# Routing plan — S043-rule-source-traceability

**Preset:** Standard — **approved** (`G2=1`)  
**Orchestrator:** 16-evolve · **Cycle:** EV-035  
**Path:** `00→16→01→02→04→07→08→09→11→12→13`  
**Skip:** `03, 05, 06` · **Optional:** `10-e2e` (no UI)  
**Branch:** `evolve/EV-035-rule-source-traceability`  
**Features:** deepen **F6 / F12 / F15 / F2** (no new Fn — `G1=2`)  
**Skills in build:** `mine-domain-sources` (re-link / promote); F29-style dense asserts

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | open S043; G1–G4 locked |
| 16-evolve | yes | orchestrator | in_progress | Phase A PASS → 04 |
| 01-requirements | yes | delta | **completed** | deepen ACs + TC-EV035 |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS (`1,1,1,1`) |
| 03-plan-tooling | no | — | skipped | existing mine-domain-sources / catalog-regen |
| 04-tech-plan | yes | delta | **completed** | Gate B PASS (`1,1,1,1`) |
| 05-verify-tech | no | — | skipped | — |
| 06-tech-tooling | no | — | skipped | — |
| 07-build | yes | full | **in_progress** | M0–M3 done; → 08 |
| 08-verify-build | yes | delta | pending | — |
| 09-qa | yes | delta | pending | TC-EV035 matrix |
| 10-e2e | no | — | skipped | no UI |
| 11-verify-impl | yes | delta | pending | — |
| 12-verify-deploy | yes | delta | pending | may waive if docs/tests only |
| 13-deploy-smoke | yes | delta | pending | AskQuestion at gate if no runtime |

## Skip rationale

Docs + domain provenance + engine cite/tests. No new Cursor rules (03), no new deps
(05/06). No browser UJ (10). Deploy (12/13) AskQuestion if no runtime surface.

## Test bar (locked)

Every rule cited or revisited → **many asserts** (TC-EV035-001..006). Gaps raised — no invent.

## Approval

| Gate | Decision | Date |
|------|----------|------|
| Phase 0 intake | Q1=3, Q2=4, Q3=1, Q4=2 | 2026-08-05 |
| Fn / routing / CORPUS / proceed | G1=2, G2=1, G3=1, G4=1 | 2026-08-05 |
| Gate A / 02 | Batch A `1,1,1,1` → PASS → 04 | 2026-08-05 |
| Gate B / 04 | Batch B `1,1,1,1` → PASS → 07 | 2026-08-05 |
