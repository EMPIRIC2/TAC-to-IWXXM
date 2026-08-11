# Session brief — S065-quality-metrics-diff-long-line

| Field | Value |
|-------|-------|
| **Type** | hotfix |
| **Intent** | Quality metrics unified XML diff renders as one long C14N line on staging; pretty-print for readable line diffs |
| **Branch** | `fix/quality-metrics-diff-long-line` (base `stage`) |
| **Orchestrator** | 14-hotfix |
| **Bug report** | [docs/bug-reports/BUG-2026-08-11-quality-metrics-diff-long-line.md](../../bug-reports/BUG-2026-08-11-quality-metrics-diff-long-line.md) |
| **GitHub** | none (staging operator report) |
| **Started** | 2026-08-11 |
| **Status** | Phase 0–1 in progress |

## Goal

Make Quality metrics Official/Converted panes and the unified XML diff human-readable by pretty-printing C14N forms before line-oriented diff (F7.q / UJ-056).

## Out of scope

- Dedicated `/quality/:stem` (or similar) detail route
- GitHub-style expand/collapse of unchanged hunks
- API / `match_status` / fixture generator changes
- Promote `stage` → `main` unless explicitly requested

## Decisions

- `D-S065-scope=4` — hotfix readability now; evolve later for separate page + hunks
- `D-S065-products=all` — all Quality metrics stems
- `D-S065-page=inline-for-now` — keep detail on current tab

## Corpus

[Corpus: product] F7.q · [Corpus: tests] UJ-056 / TC-EV055-001 · [Corpus: system-spec] Quality metrics UI
