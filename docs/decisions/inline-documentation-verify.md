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

## EV-089 disposition

| Item | Disposition |
|------|-------------|
| Delta paths (`profile_registry.py`, `convert.py`) | PASS under `VERIFY_DOC_PATHS` (missing=0) |
| OpenAPI description string edits | No new public symbols |
| Full-tree ~10k missing | **WAIVE** — brownfield baseline; same bar as EV-087/088 |

```bash
VERIFY_DOC_PATHS="packages/tac2iwxxm/src/tac2iwxxm/profile_registry.py,packages/tac2iwxxm/src/tac2iwxxm/convert.py" \
  python3 ~/.cursor/skills/bin/inline-doc-check.py .
```

## EV-091 disposition

| Item | Disposition |
|------|-------------|
| Delta paths (`DisseminationDrawer.tsx`, `FileConverter.tsx`, `operatorDisseminationUi.ts`) | PASS under `VERIFY_DOC_PATHS` (missing=0) after FileConverter TSDoc |
| Full-tree scan (default paths) | **WAIVE** for EV-091 merge — same brownfield bar as EV-087–089 (`D-EV091-inline-doc`); superseded by EV-092 for new merges |
| Remaining ~107 true gaps (after pack checker exclusions) | Closed by [#1090](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1090) / EV-092 |

```bash
VERIFY_DOC_PATHS="apps/frontend/src/app/components/DisseminationDrawer.tsx,apps/frontend/src/app/components/FileConverter.tsx,apps/frontend/src/utils/operatorDisseminationUi.ts" \
  python3 ~/.cursor/skills/pack/bin/inline-doc-check.py .
```

## EV-092 disposition

| Item | Disposition |
|------|-------------|
| Pack checker harden (multi-line TSDoc; skip `iwxxm_xsd/`/`generated/`/`*.d.ts`/`docker/`/`supabase/functions/`; Protocol/TypedDict) | **Landed** — pack `main` via EV-044 / [spec-dev-knowledge-graph#92](https://github.com/joseph-c-mcguire/spec-dev-knowledge-graph/pull/92) |
| Full-tree after harden | **scanned=541 missing=107** |
| Product NumPy/TSDoc backfill | **missing=0** |
| Full-tree `inline-documentation` implementing twin | **PASS** — no WAIVE; `D-EV091-inline-doc` superseded for new merges |

```bash
python3 ~/.cursor/skills/pack/bin/inline-doc-check.py .
# expect: missing=0
```

**Implementing twin (post EV-092):** Full-tree scan is **blocking** (not advisory) when the hardened pack checker is on PATH. Delta `VERIFY_DOC_PATHS` remains valid for non-fill evolves.
