---
session_id: S065-quality-metrics-diff-long-line
type: hotfix
status: completed
branch: fix/quality-metrics-diff-long-line
orchestrator: 14-hotfix
github_issues: []
followup_github_issue: 988
opened: 2026-08-11
closed: 2026-08-11
---

# Session brief — S065-quality-metrics-diff-long-line

| Field | Value |
|-------|-------|
| **Type** | hotfix |
| **Intent** | Quality metrics unified XML diff renders as one long C14N line on staging; pretty-print for readable line diffs |
| **Branch** | `fix/quality-metrics-diff-long-line` (base `stage`) |
| **Orchestrator** | 14-hotfix |
| **Bug report** | [docs/bug-reports/BUG-2026-08-11-quality-metrics-diff-long-line.md](../../bug-reports/BUG-2026-08-11-quality-metrics-diff-long-line.md) |
| **GitHub** | none (staging operator report); follow-up [#988](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/988) |
| **PR** | [#987](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/987) → `stage` @ `340b3cf6` |
| **Started** | 2026-08-11 |
| **Status** | **completed** (`D-S065-close=1`) |

## Goal

Make Quality metrics Official/Converted panes and the unified XML diff human-readable by pretty-printing C14N forms before line-oriented diff (F7.q / UJ-056).

## Out of scope (this session)

- Dedicated `/quality/:stem` (or similar) detail route → **S066 / EV-056 / #988**
- GitHub-style expand/collapse of unchanged hunks → **S066**
- API / `match_status` / fixture generator changes
- Promote `stage` → `main` unless explicitly requested

## Decisions

- `D-S065-scope=4` — hotfix readability now; evolve later for separate page + hunks
- `D-S065-products=all` — all Quality metrics stems
- `D-S065-page=inline-for-now` — keep detail on current tab
- `D-S065-pr=1` — PR #987 → stage
- `D-S065-close=1` — merge #987; close session; open S066 Lean evolve for #988

## Corpus

[Corpus: product] F7.q · [Corpus: tests] UJ-056 / TC-EV055-001 · [Corpus: system-spec] Quality metrics UI

## Follow-up

[FOLLOWUP.md](./FOLLOWUP.md) → **S066 / EV-056** / [#988](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/988)
