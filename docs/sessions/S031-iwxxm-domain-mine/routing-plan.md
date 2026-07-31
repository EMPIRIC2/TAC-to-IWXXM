# Routing plan — S031-iwxxm-domain-mine

**Preset:** Lean+build (+ **13 when catalog/API behavior ships**) — **approved** E24-3 / E24-4  
**Orchestrator:** 16-evolve · **Cycle:** EV-024  
**Path:** `00→16→01→02→04→07→08→10` (+ `13` if UI catalog or API surface ships)  
**Skip:** `03, 05, 06, 09, 12` (re-add if 04 introduces new deps/ADR tooling); **11** optional  
**Skills in build:** `mine-domain-sources`, `extract-pdf-to-repo` (#773)

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | Session open; Phase 0 locked E24-1..4 |
| 16-evolve | yes | orchestrator | **in_progress** | EV-024 Phase 0–1 locked; next 01 |
| 01-requirements | yes | delta | **in_progress** | E24-M=M3, E24-C hybrid; report 01-requirements.md — pending close → 02 |
| 02-verify-plan | yes | delta | pending | Gate A |
| 04-tech-plan | yes | delta | pending | Execution plan: mine → wire → promote → child issues |
| 07-build | yes | full | pending | Mining notes + fixture/catalog + promotions |
| 08-verify-build | yes | delta | pending | — |
| 09-qa | no | — | skipped | 08+10 cover |
| 10-e2e | yes | smoke | pending | Catalog/validate/convert surfaces as wired |
| 11-verify-impl | optional | — | pending | Offer if UI catalog changes material |
| 12-verify-deploy | no | — | skipped | — |
| 13-deploy-smoke | when ships | full | pending | Only if catalog/API behavior ships to prod |

## Skip rationale

Discovery + fixture/catalog deepen on existing packages and domain corpus. No new deployable /
no new Fn. Engine gaps → child issues (not 07 encode rewrites). 13 only if operator-visible
catalog or API validate coverage ships.

## Approved

| Gate | Decision | Date |
|------|----------|------|
| Session open | S031 / `evolve/EV-024-iwxxm-domain-mine` | 2026-07-30 |
| Intake | E24-1=1a+Build, E24-2=2b (#804+#807+#773), E24-3=3a full AC, E24-4=4b Lean+build | 2026-07-30 |
| Routing | Lean+build + 13-when-ships | 2026-07-30 |
| Exclude | #806 WIS2 | 2026-07-30 |
