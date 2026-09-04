---
name: api-documentation
description: >
  Add and update NumPy-style docstrings for Python modules, classes, and functions, and TSDoc
  comments for TypeScript modules, classes, interfaces, and functions. Use when documenting code,
  writing docstrings, adding API comments, improving module docs, or when the user mentions
  numpydoc, NumPy docstrings, TSDoc, or TypeScript documentation.
---

# API Documentation

Document public Python and TypeScript APIs using project conventions below.

## When to apply

- Adding or changing **public** modules, classes, functions, methods, interfaces, or exported types
- User asks to document, add docstrings, or improve API comments
- Reviewing PRs that touch undocumented public APIs

## Scope

| Location | Standard |
|----------|----------|
| `apps/backend/**/*.py`, `packages/**/*.py` | NumPy / numpydoc |
| `apps/frontend/**/*.{ts,tsx}`, `packages/shared/**/*.{ts,tsx}`, `apps/e2e/**/*.ts` | TSDoc |
| `vendor/**` | Do not edit (read-only vendor snapshots) |
| `**/*test*`, `**/tests/**`, `**/__tests__/**` | Brief purpose doc only; no full API sections |

## Workflow

1. **Identify surface** — Document exports and public symbols only. Skip `_private` helpers unless non-obvious.
2. **Read signatures** — Match parameter names, types, defaults, and return types exactly.
3. **Draft docs** — Follow the language reference (links below).
4. **Use domain terms** — IWXXM vocabulary from `docs/feature-list.md` and `docs/spec.md` (METAR, TAC, IWXXM, GIFTs, etc.).
5. **Keep types in sync** — Doc types must match annotations; do not duplicate full type signatures in prose when types are self-explanatory.
6. **Verify** — Python: `uv run ruff check <files>`. TypeScript: `pnpm exec eslint <files>`.

## Python quick rules

- **Module**: Top-of-file `"""` with purpose, key exports, and cross-links if relevant.
- **Class**: Summary line; `Attributes`, `Methods` (if public API is non-obvious), `Raises` when applicable.
- **Function/method**: Summary line; `Parameters`, `Returns`, `Raises`, `Examples` (when behavior is non-obvious).
- **One-liners**: OK for trivial getters/setters and obvious private helpers.
- **Section headers**: NumPy underline style (`Parameters`, `----------`).

Full templates and examples: [python-numpydoc.md](python-numpydoc.md)

## TypeScript quick rules

- **Module**: Top `/** ... */` block — purpose and primary exports.
- **Exported function**: Summary; `@param` per parameter; `@returns`; `@throws` for rejected promises/errors.
- **Interface / type**: Summary on the declaration; `@remarks` for constraints; document non-obvious properties inline.
- **React component**: Document the props interface/type; keep the component JSDoc to behavior and side effects.
- **Tags**: TSDoc (`@param`, `@returns`, `@throws`, `@example`, `@remarks`) — not legacy `@return`.

Full templates and examples: [typescript-tsdoc.md](typescript-tsdoc.md)

## Do not

- Document implementation details that duplicate obvious code
- Add docs to generated files, lockfiles, or `vendor/**`
- Use Google-style `Args:` in new Python docs (use NumPy `Parameters`)
- Use `@return` in TypeScript (use `@returns`)

## Checklist

```
- [ ] Public API surface identified
- [ ] Module-level doc present (if new file or missing)
- [ ] Parameters / Returns / Raises match implementation
- [ ] Domain terms spelled per project vocabulary
- [ ] Examples only where they add clarity
- [ ] Lint passes on touched files
```
