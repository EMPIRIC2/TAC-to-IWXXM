# Session brief — S063-quality-metrics-tab

> **Cycle**: EV-054 · **Type**: feature · **Opened**: 2026-08-10  
> **Branch**: `evolve/EV-054-quality-metrics-tab` (base `stage@f2926ac8`)  
> **Orchestrator**: **16-evolve**  
> **Corpus**: [Corpus: product §F7] [Corpus: product §F25] [Corpus: journeys]
> [Corpus: tests] [Corpus: adr/ADR-032] [Corpus: adr/ADR-025] [Corpus: api]
> [Corpus: system-spec]

## Goal

Add an operator **Quality metrics** tab that browses the official WMO IWXXM example
corpus by product and surfaces match, residuals, lint, and validate diagnostics per file.

## Intent (locked — D-S063-route=1)

Ship [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836): a browsable metrics /
corpus-quality surface alongside the convert workbench (F7 deepen). Reuse catalog +
fixture inventory (`examplesCatalog`, FIXTURE_GAPS, quality matrices) rather than
re-mining WMO trees. Default view offline / bundled — no live network for the happy path.

| Decision | Choice |
|----------|--------|
| D-S063-route | **1** — Standard as drafted; branch from `stage`; #836 → In progress; → 16-evolve |
| D-S063-ui-preview | **2** — No local UI preview; docs/repo only for now |
| D-S063-scope | **1** — Full #836 scope (iterative ship OK) |
| D-S063-fn | **1** — Deepen F7 only; note F7.q (no F34) |
| D-S063-compute | **1** — Precomputed fixture/CI JSON default; on-demand refresh later |

## Out of scope

- Replacing CI residual / encode / lint matrices (#815, #831 / F29) — UI complements them
- Promoting `wmoReference` → `wmoPass` encode equality (child encode issues remain SoT)
- Live re-download of upstream WMO trees on every page load
- New products beyond catalog / F6 (+ deferred) inventory
- Mutation testing (#874), Schemathesis (#727)
- Workbench epic (#840) unless needed for a tiny deep-link
- `stage`→`main` promote unless explicitly approved later

## Features (proposed)

- Deepen **F7** (operator UI tab) — consumes F9 decode, F2 validate, F15/F20/F23+ quality
  bars, F25 / F7.g catalog ([Corpus: product])
- Optional new sub-id **F7.q** or next Fn — decide in 16-evolve Phase 1 (issue open Q3)
- Related journeys: new UJ (proposed) + deepen UJ-032 / UJ-039 / UJ-042

## Acceptance (from #836 — draft for 01)

1. Quality metrics tab reachable; lists official corpus files **by product / file type**
2. Selecting a file shows official peer + our conversion comparison (match + inspectable XML/TAC)
3. Residuals, lint, and validation issues visible (empty states when clean)
4. Product-level summary counts match underlying fixture run (or documented refresh)
5. Deferred / gap stems labeled; no silent missing in-scope official files for the pin
6. H4–H5 (or Vitest + Playwright) smoke: open tab → filter product → open passer → clean/expected diagnostics
7. No Supabase / network required for the default corpus view

## Related issues

- [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836) — this session (primary)
- Prior art: #780 examples UI, #815 residuals, #831 matrices, #804 tree mine
- ADR-032 catalog tiers; ADR-025 decode

## Board

- Project [#7 TAC-to-IWXXM](https://github.com/orgs/EMPIRIC2/projects/7)
- #836 → **In progress** (`D-S063-route=1`)
- #959 (CLOSED) board hygiene → **Done**
- Ready queue = 2 (`#948`, `#958`) — below 3–5; propose refill in 16-evolve checkpoint

## UI preview

Declined (`D-S063-ui-preview=2`) — docs/repo only; re-offer at 11-verify-impl if needed.

## Notes

- Spike in 01/04: precompute metrics JSON in CI vs on-demand convert/decode/validate
- Diff UX v1: status badge + raw panes vs unified XML diff (issue open Q2)
- Untracked local `.cursor/rules/optional/*.mdc` — leave uncommitted unless user asks
