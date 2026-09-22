# Inline documentation verify bar

**Status:** Active — **ADR-048** bar for evolve / verify twins  
**Related:** [Corpus: docstrings] [Corpus: adr/ADR-048] [Corpus: verifier] angle
`inline-documentation`; `.cursor/rules/optional/api-documentation.mdc`

## Bar (documenting) — ADR-048

In-scope product symbols under `packages/` and `apps/` (see [Corpus: docstrings]) must
meet the multi-language depth bar:

| Language | Requirement |
|----------|-------------|
| Python | NumPy on public **and** private functions/methods; public `Examples` (doctest-safe); class `Attributes` / `__init__` `Parameters` |
| TypeScript | TSDoc on exported **and** non-exported functions/classes/methods; exported **executable** `@example`; typed members documented |
| Rust | rustdoc on `pub` and private items; `pub` `# Examples` where runnable |
| Shell | `#` comment above public functions (unchanged) |

**Path exclusions:** tests, fixtures, generated, vendor, `node_modules`, `target/`,
generated `*.d.ts`.

**Symbol exemptions (PY/TS):** type-only `Protocol`/`TypedDict`/`Enum` stubs (doc the type);
generated OpenAPI/client stubs; `__getattr__` shims; listed exemption globs only if
unavoidable. **Rust `pub`:** no exemptions — runnable `# Examples` required on every `pub`
item.

Planning IDs must not appear in operator-facing OpenAPI copy ([Corpus: product §F7]).

## Implementing twin (ADR-048)

For **EV-docstring-multilang-bar**, **EV-adr048-doc-linters**, and subsequent merges after
ADR-048:

1. **Full in-scope tree** — presence + required Examples/`@example`/`# Examples` + shape
   checkers **blocking** (product make/CI; may extend pack `inline-doc-check`).
2. **Native linters (blocking)** — ruff pydocstyle (D); eslint-plugin-jsdoc; Rust
   `#![deny(missing_docs)]` (D-EVDOC-LINT-01). Neither native nor checker layer is
   advisory-only.
3. **Private PY shape** — Parameters/Returns when applicable (D-EVDOC-LINT-02).
4. **TS methods/members** — eslint-plugin-jsdoc + hardened `check_docs_ts.mjs`
   (D-EVDOC-LINT-03).
5. **Example execution** — PY doctest; Rust doctest where present; TS `@example`
   executable.
6. **Warnings/infos** — entire monorepo, all toolchains, treated as failures.
   **No temporary suppressions** — fix or reconfigure toolchains. Coverage / security /
   typecheck thresholds unchanged by EV-adr048-doc-linters.
7. **TS examples** — repo-owned harness (extract `@example` → vitest/node); fail closed.
8. Delta `VERIFY_DOC_PATHS` remains valid only for **non-fill** evolves that do not claim
   the ADR-048 bar.

```bash
# Presence (pack helper; extend in-repo for Examples/shape/TS/Rust)
python3 ~/.cursor/skills/pack/bin/inline-doc-check.py .
# Product targets (names locked in tech-plan / Makefile Build):
#   make check-docs
#   make test-doctest   # PY Examples
#   make check-docs-ts  # TSDoc + executable @example
#   make check-docs-rust
```

## Historical dispositions (pre–ADR-048)

### EV-087 … EV-091

Full-tree WAIVE / delta `VERIFY_DOC_PATHS` — **historical**. Do not reuse as merge criteria
after ADR-048 for doc-fill cycles.

### EV-092 disposition

| Item | Disposition |
|------|-------------|
| Pack checker harden | Landed (pack) |
| Public presence `missing=0` | PASS for public-only presence |
| Examples / private / TS `@example` exec / Rust doctest / warn-clean | **Out of EV-092** — owned by ADR-048 / EV-docstring-multilang-bar |

```bash
python3 ~/.cursor/skills/pack/bin/inline-doc-check.py .
# public presence helper only — not sufficient for ADR-048 acceptance
```

## EV-docstring-multilang-bar disposition

| Item | Disposition |
|------|-------------|
| Standing docs + ADR-048 | Spec band (this file + [Corpus: docstrings]) |
| Checkers + backfill + warn/info-clean | Build band after Spec→Build gate |
| TC-EVDOC-001..007 | [Corpus: tests] |
| Prior hybrid D | **Superseded** for in-scope trees |

## EV-adr048-doc-linters disposition

| Item | Disposition |
|------|-------------|
| Native linters + checker gap harden | Build after Spec→Build gate (D-EVDOC-LINT-01..03) |
| TC-EVDOC-008..010 | [Corpus: tests] |
| Coverage/security/type thresholds | Unchanged (D-EVDOC-LINT-04) |
