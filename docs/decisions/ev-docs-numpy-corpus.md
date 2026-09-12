# EV-docs-numpy-corpus — corpus slim + NumPy + archive

**Date:** 2026-09-12  
**Session:** `EV-docs-numpy-corpus`  
**Status:** Accepted (operator approved recommended defaults + sessions promote-then-archive)

## Decisions

1. **CORPUS** shrinks to an engineering spine; `domain/` is opt-in; ephemeral trees leave the default branch after archive.
2. **`docs/sessions/`:** promote live dependencies (notably S019 BYOC fixtures; S043 provenance path if still required) → move remainder to orphan branch `docs-archive` → leave a stub README. Do not blind-delete.
3. **`workflow-state.yaml`:** replace with a short stub; full blob archived on `docs-archive`.
4. **Docstrings:** NumPy for public Python APIs; hybrid D (packages exemplar + gate-forward). Policy: [engineering/docstrings.md](../engineering/docstrings.md).
5. **Standing spine** (`feature-list`, `test-plan`, etc.): stub/slim in this cycle; keep paths.

## Rationale

- Live pack sessions already use `~/.cursor/workflow/…`; in-repo `docs/sessions/` is brownfield history plus a few fixtures.
- Agent default load and clone size are dominated by sessions/ARCHIVE/evolve-reports and a multi-MB `workflow-state.yaml`.
- scientific-agent-skills patterns (progressive disclosure, evidence-bound claims, Mermaid-first) inform writing quality without importing their skill tree.

## Follow-ups (Build)

See session `reports/requirements.md` acceptance A–E.
