# Routing plan — S065-quality-metrics-diff-long-line

| Field | Value |
|-------|-------|
| **Preset** | Lean |
| **auto_lean** | true |
| **Rationale** | Hotfix UX readability; no API/arch; deferred page+hunks to evolve |

## Stages

| Stage | Status | Notes |
|-------|--------|-------|
| 00-context | completed | Session open |
| 14-hotfix | in_progress | BUG + pretty-print C14N display/diff |
| 15-service-health | optional | Only if user asks after staging deploy |

## Follow-up (not this session)

Lean **16-evolve** deepen F7.q: dedicated detail page + GitHub-style collapsible hunks.
