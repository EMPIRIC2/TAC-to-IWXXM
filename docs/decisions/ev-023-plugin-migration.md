# EV-023 — TAC plugin migration decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-08-24 | Archive numbered `00–19` + `pipeline` to `.cursor/skills/_archive/` | Pack skills from engineering-memory plugin |
| 2026-08-24 | Remove pack duplicate support skills from live tree | Plugin provides `support-*` flat skills |
| 2026-08-24 | Keep `mine-domain-sources`, `monorepo-migration-checklist` | TAC-specific; excluded from pack |
| 2026-08-24 | Keep TAC-customized cross-cutting `.md` refs | connectivity-gates, deployment-catalog, considerations |
| 2026-08-24 | New sessions → `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` | Pack session-store-path rule |
| 2026-08-24 | `workflow-state.yaml` retained for brownfield in-flight only | No forced migration of active legacy state |
| 2026-08-24 | EV-024: graph ingest + `resolve-project-id` fix | Corpus (9 docs) + 50 commits; cross-workspace git root resolution |
| 2026-08-24 | Closeout on `stage` @ `8abc5996` | CI run 32780786432 SUCCESS (Deploy stage + Staging smoke) |

[Corpus: skill-placement]
