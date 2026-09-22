# ADR-048: Multi-language inline documentation bar

**Status:** Accepted  
**Date:** 2026-09-22  
**Session:** EV-docstring-multilang-bar  
**Corpus:** [Corpus: docstrings] [Corpus: decisions/inline-documentation-verify] [Corpus: tests] [Corpus: tech-spec]

## Context

Standing policy was **hybrid D** ([Corpus: docstrings]): NumPy on public Python APIs,
one-line private helpers, exemplar packages + gate-forward `VERIFY_DOC_PATHS`, optional
Examples. EV-092 made public presence (`inline-doc-check`) blocking for merges, but did
**not** require Examples/doctests, private NumPy sections, TypeScript `@example`, or Rust
`missing_docs` + doctests. Maintainers and CI need a single fail-closed bar across
**Python, TypeScript, and Rust** product source under `packages/` and `apps/`.

## Decision

1. **Supersede hybrid D** for in-scope product trees. Hybrid D remains historical only.

2. **In scope**
   - Python: `packages/*/src`, `apps/backend`, `apps/worker`
   - TypeScript/TSX: `apps/frontend`, shipping `apps/e2e` helpers
   - Rust: `packages/*/rust/src` (`tac2iwxxm`, `iwxxm-validate`)
   - **Exclude:** tests, fixtures, generated, vendor, `node_modules`, `target/`, generated `*.d.ts`

3. **Depth**
   - **PY:** NumPy on all public **and** private functions/methods; public APIs require
     doctest-safe `Examples`; classes document `Attributes` / `__init__` `Parameters`;
     private may omit `Examples`.
   - **TS:** TSDoc on exported **and** non-exported functions/classes/methods; exported
     require **executable** `@example`; interfaces/types document members.
   - **Rust:** rustdoc on all `pub` and private `fn`/`struct`/`enum`/`impl`; `pub` items
     require `# Examples` doctests where runnable.

4. **Symbols:** Same bar for nested functions, methods, React components/hooks, Rust
   `impl` methods. **Exempt (PY/TS only):** type-only `Protocol`/`TypedDict`/`Enum` stubs
   (document the type); generated OpenAPI/client stubs; `__getattr__` shims; listed
   exemption globs only if unavoidable. **Rust:** no exemptions for `pub` items — every
   `pub` item must have runnable `# Examples` (verified at verify-plan S14).

5. **Checkers (product repo):** Makefile targets + tests under `tests/` and/or
   `packages/*/tests`, extending pack `inline-doc-check` where useful; CI on PR. Fail closed
   on missing docs, missing required examples, and required shape. Preferred target names
   (locked in tech-plan): `check-docs`, `test-doctest`, `check-docs-ts`, `check-docs-rust`.

6. **Example execution:** Public PY `Examples` via doctest; every Rust `pub` `# Examples`
   runnable; TS `@example` via **repo-owned harness** (extract → vitest/node), fail closed
   if missing or failing.

7. **Quality pass:** Lint + format + typecheck + unit for the **entire monorepo / all
   toolchains** treat **warnings and infos as failures**, delivered in **one PR** with the
   doc bar work. **No temporary suppressions** — fix or reconfigure toolchains (verify-plan
   S12).

8. **Must-not-break:** convert/validate/decode/disseminate HTTP+CLI behavior; operator
   OpenAPI copy; pack-engine wire shapes. No new Fn; no H4–H5/UI this cycle.

## Consequences

- Larger one-PR blast radius (docs backfill + warning burn-down).
- New/extended make + CI targets; possible new lint deps → update dependency-inventory.
- Pack `inline-doc-check` alone is insufficient; product checkers own Examples/shape/TS/Rust.
- Prior full-tree WAIVEs (EV-087–091) do not apply to this cycle’s merge criteria.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Keep hybrid D + delta `VERIFY_DOC_PATHS` | Does not meet operator ask (Examples, private, TS/Rust, warn-clean) |
| Exemplar packages only | Explicitly rejected — all product `packages/` + `apps/` |
| Presence-only TS `@example` | Rejected — executable `@example` required |
| Warnings-as-errors on in-scope trees only | Rejected — entire monorepo zero warn/info in one PR |

## Related

- [Corpus: docstrings] · [Corpus: decisions/inline-documentation-verify]
- Session: `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-docstring-multilang-bar/`
- Decisions: `docs/decisions/evolve-decisions.md` (D-EVDOC-*)
- Tests: TC-EVDOC-001..007
