# Follow-up — Quality metrics GitHub-style diff page

**Deferred from:** S065 / BUG-2026-08-11 (`D-S065-scope=4`)  
**When ready:** open **00-context** → session type `feature` → **16-evolve** Lean (UX/docs/tests; no API unless needed)  
**Corpus:** [Corpus: product] F7.q · [Corpus: tests] UJ-056 · deepen Quality metrics UX  
**Depends on:** this hotfix merged to `stage` (pretty-printed C14N display/diff)

## Goal

Replace the inline Quality metrics detail+diff with a dedicated, readable inspection surface:

1. **Separate page / route** for a stem (e.g. `/quality/:stem` or equivalent shell route) with back-to-list
2. **Pretty XML** panes (already partially done by S065 — keep/extend)
3. **GitHub-style unified diff** — collapse/expand unchanged context around change hunks (default collapsed with N lines of context; expand hunk / expand all)

## Out of scope (unless decided otherwise)

- Changing `match_status` / C14N equality / fixture generator
- New npm diff library unless AskQuestion approves (today: LCS in `unifiedLineDiff.ts`)
- Promote to `main` until Staging smoke + gate

## Suggested acceptance

| ID | Criterion |
|----|-----------|
| AC1 | List row opens a dedicated detail route (shareable URL) |
| AC2 | Official/Converted/TAC panes remain; normalized = pretty C14N |
| AC3 | Diff shows collapsible equal-context hunks (GitHub-like `@@` / “Expand N lines”) |
| AC4 | Unequal SIGMET stems remain navigable and readable on staging |
| AC5 | UJ-056 / TC-EV054–055 updated; FE unit + optional Playwright smoke |

## Seed prompt (paste into next session)

```
/00-context then /16-evolve Lean — F7.q deepen:

After S065 pretty-print hotfix, add a dedicated Quality metrics detail page
with GitHub-style collapsible unified XML diffs (expand/collapse unchanged
context). Keep C14N equality semantics; no API contract change unless needed
for routing. Base stage. Cite UJ-056 / F7.q. Follow-up from
docs/sessions/S065-quality-metrics-diff-long-line/FOLLOWUP.md
```

## Implementation notes

- Reuse `unifiedLineDiff` + `qualityMetricsDisplayXml` / `prettyPrintXml`
- Add hunk folding helper (e.g. `collapseEqualContext(lines, { context: 3 })`)
- Wire route in frontend shell next to Quality metrics tab
- Operator copy: no internal doc refs (EV-048)
