# Workflow-state agent protocol (skills 00–19)

**Mandatory for every pipeline skill.** Do not duplicate this file in full — link from SKILL.md.

**Agent:** [workflow-state-manager](../agents/workflow-state-manager.md) — **sole writer** of
repo-root [`workflow-state.yaml`](../../workflow-state.yaml). Skills **must not** read or edit
that file directly.

**Schema:** [workflow-state-reference.md](workflow-state-reference.md)

**Sessions:** [sessions-reference.md](sessions-reference.md)

---

## On invocation (mandatory first action)

1. Invoke **workflow-state-manager** with:
   ```yaml
   operation: read_context
   skill_id: <this skill's directory name>
   user_intent: <verbatim user goal if any, e.g. "add features X, Y, Z">
   mode: <greenfield | delta | evolve — optional>
   session_id: <from active_session.id if resuming; optional on 00 open>
   evolve_context: <optional; from 16-evolve parent>
   ```
2. Read the agent's **context brief**. If `blocking: true` or **Blocking deviations** listed:
   - Present to user via **AskQuestion** with agent evidence
   - **Do not start work** until resolved or user explicitly waives
3. **Session gate (stages 01–19):** If `active_session` is null, agent blocks — route to
   [00-context](00-context/SKILL.md) to open or resume a session (unless user waives orchestration
   via AskQuestion; record in `decisions_log`).
4. **Routing gate:** If current `skill_id` not in `active_session.routing_plan`, agent warns —
   AskQuestion to amend plan or waive.
5. If user requests **feature addition** or **large change** with no active session, agent
   recommends **00-context** → session type `feature` → [16-evolve](16-evolve/SKILL.md).

## During work

After **each substep** that changes stage progress, artifacts, gates, git history, sessions, or cycles:

```yaml
operation: update
skill_id: <this skill>
session_id: <active_session.id when set>
update_payload: { ... }
```

Never buffer updates across substeps.

Session reports: write under `active_session.artifacts_dir/reports/`; append to `artifacts[]`
with `session_id` tag.

## On completion

Final agent `update` with stage `status: completed` (or `failed` / `skipped`), timestamps, and
artifact paths. Update `active_session.routing_plan` entry for this stage. Mirror completion in
`project.stages.{key}` when applicable.

**Session close:** When all routing-plan stages complete, orchestrator or 00 runs checkpoint
AskQuestion, archives to `sessions[]`, sets `active_session: null`.

Detail trackers (`workflow-state.yaml + execution plan artifact`, session reports, etc.) must
agree with agent state.

## Feature addition at any stage

Any skill **00–15** may receive "add features X, Y, Z" during an **active session** with type
`feature` or `new_service` and an active evolve cycle. Run **§Delta / feature-addition mode**.
Without a session, route through **00-context** first.

Default: **one session, one evolve cycle, multiple Fn** per user request when appropriate.
