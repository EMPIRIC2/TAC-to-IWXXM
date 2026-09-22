# Engineering — multi-language documentation bar

[Corpus: docstrings] [Corpus: adr/ADR-048]  
See also [inline-documentation-verify.md](../decisions/inline-documentation-verify.md).

**Policy authority:** [ADR-048](../adr/ADR-048-multilang-inline-documentation-bar.md)
(**Accepted**). Hybrid D (exemplar + gate-forward; private one-liners; optional Examples) is
**superseded** for in-scope product trees.

## In scope

| Language | Paths |
|----------|--------|
| Python | `packages/*/src`, `apps/backend`, `apps/worker` |
| TypeScript/TSX | `apps/frontend`, shipping `apps/e2e` helpers |
| Rust | `packages/*/rust/src` (`tac2iwxxm`, `iwxxm-validate`) |

**Exempt paths:** tests, fixtures, generated, vendor, `node_modules`, `target/`, generated
`*.d.ts`.

## Python (NumPy)

All public **and** private functions/methods use **NumPy** docstrings. Public APIs require
doctest-safe `Examples`. Classes document `Attributes` and `__init__` `Parameters` as
applicable. Private helpers may omit `Examples`.

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

Examples
--------
>>> example_call()
'ok'
"""
```

| Surface | Requirement |
|---------|-------------|
| Module | One-line or short module docstring |
| Public function / method / class | Full NumPy + `Examples` (doctest-safe) |
| Private helpers (`_foo`) | NumPy sections as applicable; `Examples` optional |
| Class attributes | `Attributes` section (and/or `__init__` `Parameters`) |
| Tests / fixtures / generated / vendor | Exempt |

**Comments:** explain *why*, fail-closed behavior, or non-obvious invariants — not the next
line of code.

## TypeScript (TSDoc)

TSDoc on **exported and non-exported** functions, classes, and methods. Exported symbols
require an **executable** `@example` block. Interfaces and type aliases document members.

## Rust (rustdoc)

rustdoc (`///`) on all `pub` and private `fn` / `struct` / `enum` / `impl` items. Public
items require `# Examples` doctests where runnable. Prefer `#![deny(missing_docs)]` (or
equivalent crate lint) on in-scope crates.

## Symbol rules

- **Same bar:** nested functions, methods, React function components/hooks, Rust `impl`
  methods.
- **Exempt (PY/TS only):** type-only `Protocol` / `TypedDict` / `Enum` stubs (document the
  type); generated OpenAPI/client stubs; `__getattr__` shims; listed exemption globs only
  if unavoidable.
- **Rust:** no `pub` exemptions — every `pub` item needs runnable `# Examples`.

## Enforcement

1. Product-repo make targets + tests (`tests/`, `packages/*/tests`) fail closed on missing
   docs, missing required examples, and required shape (extend pack `inline-doc-check`
   where useful). Preferred: `check-docs`, `test-doctest`, `check-docs-ts`,
   `check-docs-rust` (exact names in tech-plan).
2. CI on PR runs the checkers (TC-EVDOC-*).
3. Public PY `Examples` via doctest; Rust `pub` doctests all runnable; TS `@example` via
   repo-owned harness (vitest/node), fail closed if missing or failing.
4. Lint + format + typecheck + unit across the **entire monorepo / all toolchains** treat
   **warnings and infos as failures** (same PR as the doc bar). **No suppressions** — fix
   or reconfigure toolchains.

## Must-not-break

Convert / validate / decode / disseminate HTTP+CLI behavior; operator-visible OpenAPI copy;
pack-engine wire shapes. Do not put planning IDs in operator-facing strings.

## Out of scope for agent load

Do not cite `docs/sessions/` as the docstring policy source. Live session artifacts live
under `~/.cursor/workflow/…`.
