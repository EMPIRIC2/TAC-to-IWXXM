# Pipeline protocol card (read once)

Short shared rules for **pack orchestrators** and phase skills. Prefer this over re-reading full considerations on every hop.

**Full detail (open only on failure / resume / gate):** [considerations.md](considerations.md), [connectivity-gates.md](connectivity-gates.md).

**Which skill?** → engineering-memory plugin Customize (`evolve`, `brownfield`, `greenfield`, `hotfix`, `spec-*`, `build-*`)  
**Docs truth** → [docs/CORPUS.md](../../docs/CORPUS.md) — cite `[Corpus: <id>]`.  
**Session store** → `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/{id}/` (`state.yaml`, `routing-plan.md`, `HANDOFF.md`). See [.cursor/MIGRATED-TO-PLUGIN.md](../../MIGRATED-TO-PLUGIN.md).

---

## First actions (every stage)

1. **Corpus rows for this stage** (from CORPUS §Skill obligations) — not the whole `docs/` tree.
2. **Session routing-plan** at `{session}/routing-plan.md` in the workflow session store.
3. Read `state.yaml` `current_step` once at stage start (not every micro-step).
4. Open the routed plugin skill only — open `reference.md` **on resume failure, gate failure, or missing procedure**.

Do **not** `@`-attach full skill bodies in chat; invoke by skill name + routing plan.

---

## Routing presets (orchestrators)

| Orchestrator | When | Default scale |
|--------------|------|---------------|
| `evolve` | Already on pack; add/change capability | standard |
| `brownfield` | Existing code not fully on pack | standard |
| `greenfield` | No code, no corpus | full |
| `hotfix` | One surgical failure | micro |

Spec band → gate AskQuestion → Build band. Gate field: `documenting_to_implementing_gate`.

---

## State updates (batched)

- Use `session-store update` after each child skill completes.
- Refresh `HANDOFF.md` at band boundaries.
- Legacy `workflow-state.yaml` is **read-only** for in-flight brownfield sessions — do not start new pack cycles there.

---

## AskQuestion

- Batch 2–4 questions per call; first option = recommendation; last = explain.
- Categories: `[Decision]` `[Ambiguity]` `[Contradiction]` `[Uncertainty]` `[Scope Drift]`.

---

## Connectivity

Browser-facing work: honor [connectivity-gates.md](connectivity-gates.md) tiers (H0c / H0i / H4–H5).

---

## Project-only skills

| Skill | When |
|-------|------|
| `mine-domain-sources` | Domain mining → `docs/domain/` |
| `monorepo-migration-checklist` | ADR-003 monorepo migration |

---

## Legacy (archived)

Numbered `00–19`, redirect stubs, and pack duplicates live under `_archive/`. Do not invoke for new work.
