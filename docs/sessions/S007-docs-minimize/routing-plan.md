# Routing plan — S007-docs-minimize

Process session for docs tree cleanup. Default process stages (17/18/19) do not fit;
custom `docs-execute` stage carries the moves.

| Stage | Required | Mode | Status | Skip rationale |
|-------|----------|------|--------|----------------|
| 00-context | yes | scoped | completed | Session open + layout approval |
| docs-execute | yes | full | completed | Moves + link updates + README |
| 18-pr-review | no | full | pending | Optional after PR |

## Skipped

| Stage | Rationale |
|-------|-----------|
| 01–16 | Not product/feature/hotfix/deploy work |
| 17-retrospective | Not a retro |
| 19-address-pr-review | Only if 18 finds issues |

## Approved

User approval recorded: 2026-07-12 (option 1 — conservative layout)
