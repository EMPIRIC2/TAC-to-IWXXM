# Routing plan — S001-convert-send-buttons

**Session type:** `feature`  
**Orchestrator:** [16-evolve](../../.cursor/skills/16-evolve/SKILL.md)  
**Proposed branch:** `feat/S001-convert-send-buttons`

| Stage | Required | Mode | Skip rationale |
|-------|----------|------|----------------|
| 00-context | yes | scoped | This session — `docs/context/convert-send-buttons.md` |
| 16-evolve | yes | delta | Register UI capability; update feature-list / user-journey / test-plan deltas |
| 07-build | yes | full | Implement Convert&Send in `FileConverter` + shared upload helper |
| 08-verify-build | yes | full | Lint, typecheck, unit tests |
| 09-qa | yes | full | Manual QA checklist for dual-button workflow |
| 10-e2e | yes | delta | Extend Playwright upload/convert specs |
| 11-verify-impl | yes | full | Implementation verification vs evolve artifact |
| 01-requirements | skip | — | Standing requirements exist; delta via 16-evolve |
| 02-verify-plan | skip | — | No product-plan change beyond evolve delta |
| 03-plan-tooling | skip | — | No new tooling |
| 04-tech-plan | skip | — | No new architecture; frontend-only |
| 05-verify-tech | skip | — | N/A for UI-only delta |
| 06-tech-tooling | skip | — | N/A |
| 12-verify-deploy | skip | — | Defer until PR merge / user requests deploy verify |
| 13-deploy-smoke | skip | — | Defer until deploy |

## Approved

User approval recorded: 2026-06-22

- Routing: approved as proposed
- R1: fixed upload defaults, one-click send
- R2: keep Convert + Convert&Send + Upload to Database
- R3: #656 scope only
