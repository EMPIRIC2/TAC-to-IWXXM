# Routing plan — S022-rename-cutover

**Type:** ops · **Orchestrator:** 15-service-health  
**Issue:** [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781)  
**Preset:** Ops override (`00 → 15 → 13`) — not product Lean/Standard evolve

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | session | completed | Opened 2026-07-27; routing approved (option A/1) |
| 15-service-health | yes | full | completed | Cutover PASS 2026-07-27; H0c/H1/H4/H5; goldens in bundle |
| 13-deploy-smoke | yes | full | completed | H0c/H1/H4/H5 + live UJ-032 PASS 2026-07-27 |
| 16-evolve | no | — | skipped | No product Fn / no evolve cycle |
| 01–12 (except 13) | no | — | skipped | No requirements/tech-plan/build; ops infra only |
| 14-hotfix | no | — | skipped | Unless cutover surfaces a code bug → open BUG + 14 |

## Skip rationale

- **No 16-evolve / 01 / 02 / 04 / 07**: Issue is ops rename cutover; in-repo CI/branding already done; remaining work is platform (Render, GHCR, secrets, PyPI) + smoke.
- **15 before 13**: Inventory + retarget imagePath/repo, then redeploy/smoke with connectivity gates.
- **13 required**: S021 waived live goldens to this ticket; must not close without H4–H5 PASS or explicit new waiver.
- **14 only on demand**: Code regressions found live → bug-investigation → hotfix session.

## Standing docs (delta if needed)

| Doc | When |
|-----|------|
| `[Corpus: tech-spec]` → `docs/deploy.md` / deploy-state | After Render imagePath live |
| Session reports | `docs/sessions/S022-rename-cutover/reports/` |

## Approval

**Approved** 2026-07-27 — user option A/1 (`D-S022-00-approve-routing`). Full #781 scope.
