# Workflow-state agent protocol (skills 00–19)

**Mandatory for every pipeline skill.** Do not duplicate this file in full — link from SKILL.md.

**Agent:** [workflow-state-manager](../agents/workflow-state-manager.md) — **sole writer** of
repo-root [`workflow-state.yaml`](../../workflow-state.yaml). Skills **must not** read or edit
that file directly.

**Schema:** [workflow-state-reference.md](workflow-state-reference.md)

---

## On invocation (mandatory first action)

1. Invoke **workflow-state-manager** with:
   ```yaml
   operation: read_context
   skill_id: <this skill's directory name>
   user_intent: <verbatim user goal if any, e.g. "add features X, Y, Z">
   mode: <greenfield | delta | evolve — optional>
   evolve_context: <optional; from 16-evolve parent>
   ```
2. Read the agent's **context brief**. If `blocking: true` or **Blocking deviations** listed:
   - Present to user via **AskQuestion** with agent evidence
   - **Do not start work** until resolved or user explicitly waives
3. If user requests **feature addition** or **large change** and no active evolve cycle, agent
   will block — route to [16-evolve](16-evolve/SKILL.md) unless user waives orchestration
   (record in `decisions_log` via agent).

## During work

After **each substep** that changes stage progress, artifacts, gates, git history, or cycles:

```yaml
operation: update
skill_id: <this skill>
update_payload: { ... }
```

Never buffer updates across substeps.

## On completion

Final agent `update` with stage `status: completed` (or `failed` / `skipped`), timestamps, and
artifact paths. Detail trackers (`workflow-state.yaml + execution plan artifact`, etc.) must agree with agent state.

## Feature addition at any stage

Any skill **00–15** may receive "add features X, Y, Z" or a large-change request during an
active evolve cycle. When an **evolve cycle** is active, run this skill's **§Delta /
feature-addition mode**. Otherwise follow agent routing to **16-evolve**.

Default: **one evolve cycle, multiple Fn** per user request.
