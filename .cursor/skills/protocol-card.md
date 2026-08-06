# Pipeline protocol card (read once)

Short shared rules for stages **00–19**. Prefer this over re-reading full preamble /
considerations / state-reference on every hop.

**Full detail (open only on failure / resume / gate):** [pipeline-preamble.md](pipeline-preamble.md),
[considerations.md](considerations.md), [workflow-state-agent-protocol.md](workflow-state-agent-protocol.md),
[sessions-reference.md](sessions-reference.md), [connectivity-gates.md](connectivity-gates.md).

**Which skill?** → [docs/skill-routing.md](../../docs/skill-routing.md)  
**Docs truth** → [docs/CORPUS.md](../../docs/CORPUS.md) — cite `[Corpus: <id>]`.

---

## First actions (every stage)

1. **Corpus rows for this stage** (from CORPUS §Skill obligations) — not the whole `docs/` tree.
2. **Session routing-plan** entry for this stage (`docs/sessions/{id}/routing-plan.md`).
3. **workflow-state-manager** `read_context` once at stage start (not every micro-step).
4. Open this stage’s `SKILL.md` only — open `reference.md` / preamble **on resume failure, gate failure, or missing procedure**.

Do **not** `@`-attach full skill bodies in chat; invoke by skill name + routing plan.

---

## Routing presets (00 / 16)

| Preset | Stages (typical) | Default when |
|--------|------------------|--------------|
| **Lean** | `00 → 16 → 01 → 02 → 10 → 13` | UX/docs/tests; no API/arch (existing app) |
| **Standard** | Lean + `04 → 07 → 08 → 09 → 11 → 12` | New Fn / contract change |
| **Full** | Standard + `03` / `05` / `06` as needed | New guardrails, stack change, or greenfield |

AskQuestion: recommend **Lean** for existing apps unless user picks Standard/Full.

---

## State updates (batched)

- **One** `update` at stage **start** (status `in_progress`) and **one** at stage **exit**
  (status + commits + artifacts + routing_plan row).
- Append-only `git_history.commits` may batch with the exit update.
- Do **not** spawn a Task/subagent per micro-event.
- Schema / open_session / close_session / complex cycle edits still use workflow-state-manager.

---

## AskQuestion

- Batch 2–4 questions per call; first option = recommendation; last = explain.
- Categories: `[Decision]` `[Ambiguity]` `[Contradiction]` `[Uncertainty]` `[Scope Drift]`.
- Lean plans: skip phase-checkpoint AskQuestions unless a **gate fails**.

---

## Connectivity

Browser-facing work: honor [connectivity-gates.md](connectivity-gates.md) tiers for this stage
(H0c / H0i / H4–H5). Hybrid static+API is never “API-only done.”

---

## Plan ↔ Agent loop (04 / 07 / 16)

- **16-evolve:** Plan mode = **default orchestrator** (Phase 0–1 + re-routes); Agent runs
  child stages. Evolve Plan Card: `docs/sessions/{id}/evolve-plan-card.md`.
- **04 / 07:** Plan refines execution structure / next milestone batch; Agent implements.
  Build Plan Card: `docs/sessions/{id}/build-plan-card.md`.
- See [plan-mode-loop.md](plan-mode-loop.md). Do not SwitchMode → Plan from 01–03, 05–06, 08–15.

---

## Legacy skills

Do not invoke: `gather-context`, `doc-planner`, `build-planner`, `build-executor`,
`verify-build`, `audit-docs`, `deploy-verify`. Use numbered **00–13** (stubs redirect;
full text under `_archive/`).
