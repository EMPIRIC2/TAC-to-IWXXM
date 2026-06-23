# Sessions index

Session-specific artifacts for bounded work units. Standing project docs remain in `docs/` root.

**Convention:** [sessions-reference.md](../../.cursor/skills/sessions-reference.md)  
**Routing:** [skill-routing.md](../skill-routing.md)

## Quick start

```
@00-context I want to <your goal>
```

00-context will:

1. Classify session type (`greenfield`, `feature`, `hotfix`, `integration`, `new_service`, `ops`, `process`)
2. Allocate the next id (`S001`, `S002`, …)
3. Create this folder with `session-brief.md` and `routing-plan.md`
4. Ask you to approve the routing plan
5. Set `active_session` in `workflow-state.yaml`

Then invoke stages from the approved plan (e.g. `@10-e2e`, `@16-evolve`).

## Index

| Session ID | Type | Status | Intent | Branch | Started | Completed |
|------------|------|--------|--------|--------|---------|-----------|
| [S001-convert-send-buttons](S001-convert-send-buttons/session-brief.md) | feature | completed | Convert & Convert&Send UI (#656) | feat/S001-convert-send-buttons | 2026-06-22 | 2026-06-22 |
| [S002-issue-594-feedback](S002-issue-594-feedback/session-brief.md) | hotfix | in_progress | COR handling + TAC traceability (#594) | fix/S002-issue-594-feedback | 2026-06-22 | — |

## Active session

**S002-issue-594-feedback** — see `workflow-state.yaml` §`active_session`.

## Folder layout

```
docs/sessions/SNNN-slug/
  session-brief.md      # intent, type, scope, links to standing docs
  routing-plan.md       # approved stage list + skip rationale
  reports/              # qa-report, e2e-report, verification-report, etc.
  checkpoints/          # optional phase gate digests
```

## Standing docs vs session reports

| Kind | Location |
|------|----------|
| Long-lived specs | `docs/spec.md`, `feature-list.md`, `test-plan.md`, `deploy.md`, … |
| Session outputs | `docs/sessions/{id}/reports/*.md` |
| Scoped discovery | `docs/context/{slug}.md` |

Pre-session reports at `docs/` root (e.g. `docs/qa-report.md`) are historical; new work uses
session report paths.
