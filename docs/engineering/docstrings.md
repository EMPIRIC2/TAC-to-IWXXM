# Engineering — Python / TS documentation bar

[Corpus: decisions] See also [inline-documentation-verify.md](../decisions/inline-documentation-verify.md).

## Python (NumPy)

Public modules, classes, and functions in `packages/` and `apps/` **src** use **NumPy** docstrings:

```text
"""Short summary.

Longer description when needed.

Parameters
----------
name : type
    Description.

Returns
-------
type
    Description.
"""
```

| Surface | Requirement |
|---------|-------------|
| Module | One-line or short module docstring |
| Public API | Full NumPy (Parameters / Returns / Raises as applicable) |
| Private helpers (`_foo`) | One-line purpose is enough |
| Tests / fixtures / generated / vendor | Exempt |

**Comments:** explain *why*, fail-closed behavior, or non-obvious invariants — not the next line of code.

## TypeScript

TSDoc on exported functions/classes (existing bar).

## Enforcement (hybrid D)

1. **Exemplar:** bring `tac2iwxxm`, `tac-validate`, `iwxxm-validate` (+ optionally `dissemination`, `workflows`) to the NumPy bar.
2. **Gate-forward:** evolve / PRs set `VERIFY_DOC_PATHS` (or equivalent) so new public symbols cannot land undocumented.
3. Full-tree undocumented backlog remains advisory until explicitly scheduled.

## Out of scope for agent load

Do not cite `docs/sessions/` as the docstring policy source.
