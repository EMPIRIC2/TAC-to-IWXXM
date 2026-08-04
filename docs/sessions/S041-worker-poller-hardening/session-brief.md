---
session_id: S041-worker-poller-hardening
type: feature
status: in_progress
branch: evolve/EV-033-worker-poller-hardening
started_at: 2026-08-04
intent: "Harden F8 worker INGEST_POLLER_URL cutover (prevention 1-5 + code guard)"
orchestrator: 16-evolve
evolve_cycle_id: EV-033
prior_session: S040-iwxxm-corpus-quality
context_briefs: []
standing_docs_touched: []  # filled after 01/04
feature_ids: []
deepen_feature_ids: [F8]
feature_note: "D-S041-open — F8 deepen INGEST_POLLER_URL hardening"
ask_question: unavailable — chat proceed recorded as D-S041-open
---

# Session S041 — worker-poller-hardening

## Intent

Harden F8 `metar-worker` **`INGEST_POLLER_URL`** cutover so bad/missing poller config
fail closed in ops, CI, docs, and code — without mixing into S040 corpus work.

## Prior session

| Item | Disposition |
|------|-------------|
| S040 / EV-032 | **Suspended** (not completed/cancelled) at `13-deploy-smoke` / T4.5 — resume after S041 |
| EV-032 | Remains `in_progress` |

## Scope (locked — D-S041-open = proceed_1-5_plus_code)

### In

1. Fail-closed scale when poller URL unset/placeholder
2. CI preflight for worker poller URL
3. Docs default fixture URL (no `REPLACE_ME` as runnable default)
4. No stale Render copy of poller URL guidance
5. CrashLoop alert when worker dies on bad poller URL
6. **Code guard** — reject `REPLACE_ME` / non-https poller URLs

### Out

- Completing S040 deploy smoke / #848 merge (resume later)
- Unrelated F8 ingest product changes

## Routing

**Preset:** Standard — `00→16→01→02→04→07→08→09→10→11→12→13`  
**Skip:** `03, 05, 06` unless 04 surfaces new deps/tooling  
See [routing-plan.md](routing-plan.md).

## Branch note

`evolve/EV-033-worker-poller-hardening` recorded in `git_history.branches` (`pending_create`).
Workflow-state-manager did **not** create or check out the branch.

## Links

- Standing: [feature-list.md](../../feature-list.md) (F8), [tech-spec.md](../../tech-spec.md), [CORPUS.md](../../CORPUS.md)
- Prior: [S040 session-brief](../S040-iwxxm-corpus-quality/session-brief.md)
