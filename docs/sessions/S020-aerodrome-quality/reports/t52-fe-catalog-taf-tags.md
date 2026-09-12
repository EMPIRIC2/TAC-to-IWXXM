# T5.2 — FE catalog panel filters/copy for TAF (E15-14 / UJ-031)

**Session**: S020-aerodrome-quality · **Cycle**: EV-015 · **Date**: 2026-07-22

## Result

**GREEN** — additive FE extension turns T5.1 Vitest contract green (TC-F20-005).

| Change | Detail |
|--------|--------|
| `lintIssueCatalog.ts` | Export `filterCatalogByTag`, `formatCatalogEntryCopy` |
| `WorkbenchConsole.tsx` | Tag `<select data-testid="lint-issue-catalog-tag-filter">`; list rows `lint-issue-catalog-entry-{CODE}` with enriched copy; toggle count = filtered size |

## Verification

```text
pnpm exec vitest run \
  src/utils/lintIssueCatalog.test.ts \
  src/app/components/WorkbenchConsole.catalog-taf.test.tsx \
  src/app/components/WorkbenchConsole.catalog.test.tsx \
  src/app/components/WorkbenchConsole.test.tsx
# 4 files / 13 tests passed
```

## Next

T5.3 — API smoke `product=taf` + `product=speci` lint+convert + catalog GET. Evolve PR still waits until M5 / Phase D.
