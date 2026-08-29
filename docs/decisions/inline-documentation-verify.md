# Inline documentation verify bar (EV-025 / pack angle)

**Status:** Active for evolve / verify twins  
**Related:** [Corpus: verifier] pack angle `inline-documentation`; `.cursor/rules/optional/api-documentation.mdc`

## Bar (documenting)

Public product symbols in `apps/` and `packages/` (excluding tests, fixtures, generated, vendor) must carry:

| Language | Requirement |
|----------|-------------|
| Python | Module / public class / public function NumPy-style docstrings |
| TypeScript | TSDoc on exported functions/classes |
| Shell | `#` comment above public functions |

Planning IDs must not appear in operator-facing OpenAPI copy ([Corpus: product §F7 / EV-048]).

## Implementing twin (brownfield)

Full-tree `inline-doc-check.py` over this monorepo reports **thousands** of pre-existing gaps. Until a dedicated docstring/TSDoc fill cycle:

1. **Delta gate (blocking for evolve):** set `VERIFY_DOC_PATHS` to changed product source paths and require **zero** new undocumented public symbols.
2. **Full-tree scan:** advisory / waived for merge unless the cycle’s goal is documentation fill.
3. New public APIs introduced in a cycle must be documented in the same PR.

## EV-087 disposition

| Item | Disposition |
|------|-------------|
| Delta paths (`tac2iwxxm` convert/taf/registry + schema description edits) | PASS under `VERIFY_DOC_PATHS` |
| Full-tree ~10k missing | **WAIVE** — brownfield baseline; not in EV-087 scope |
| Router `conversion.py` pre-existing undocumented handlers | Out of scope (description-only edits) |

## EV-088 disposition

| Item | Disposition |
|------|-------------|
| Delta path `scripts/profiles/scaffold_national_profile.py` | Documented (module + public helpers NumPy-style) in PR #1086 |
| Full-tree ~10k missing | **WAIVE** — brownfield baseline; same bar as EV-087; not in EV-088 scope |

## How to re-check delta

```bash
VERIFY_DOC_PATHS="packages/tac2iwxxm/src/tac2iwxxm/convert.py,packages/tac2iwxxm/src/tac2iwxxm/products/taf.py,packages/tac2iwxxm/src/tac2iwxxm/profile_registry.py" \
  python3 ~/.cursor/skills/bin/inline-doc-check.py .
```

EV-088 scaffold delta (when checker path available):

```bash
VERIFY_DOC_PATHS="scripts/profiles/scaffold_national_profile.py" \
  python3 ~/.cursor/skills/bin/inline-doc-check.py .
```
