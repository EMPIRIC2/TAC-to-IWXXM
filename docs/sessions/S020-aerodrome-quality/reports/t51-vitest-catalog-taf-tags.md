# T5.1 — Vitest catalog panel TAF tags (E15-14 / TC-F20-005)

**Session**: S020-aerodrome-quality · **Cycle**: EV-015 · **Date**: 2026-07-22

## Result

**RED** (expected) — TDD Test task. Six failing assertions define the T5.2 contract:

| Suite | Failures |
|-------|----------|
| `lintIssueCatalog.test.ts` — TAF tag helpers | 3 (`filterCatalogByTag`, `formatCatalogEntryCopy` not exported yet) |
| `WorkbenchConsole.catalog-taf.test.tsx` | 3 (entry testids, tag filter, enriched copy) |

Existing F15 tooltip suite (`WorkbenchConsole.catalog.test.tsx` + tooltip resolver) remains green (4 passed).

## Contract for T5.2

1. Export `filterCatalogByTag(entries, tag)` and `formatCatalogEntryCopy(entry)` from `lintIssueCatalog.ts`
2. Catalog list rows: `data-testid="lint-issue-catalog-entry-{CODE}"`; copy includes tags + `product:` when set
3. `<select data-testid="lint-issue-catalog-tag-filter">` with empty = all; `taf` keeps taf-tagged rows; toggle count reflects filtered size

## Next

T5.2 — FE: extend catalog panel filters/copy for TAF (additive).
