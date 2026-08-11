# BUG-2026-08-11-quality-metrics-diff-long-line

| Field | Value |
|-------|-------|
| **Status** | fix in review — PR #987 |
| **Remediation path** | 14-hotfix S065 / PR #987 → stage |
| **Environment** | staging — https://app.staging.tac-to-iwxxm.com/ |
| **Session** | S065-quality-metrics-diff-long-line |

## Error description

On the Quality metrics tab, opening unequal stems (e.g. SIGMET `sigmet-A6-1a-TS`) shows the unified XML diff as a handful of extremely long lines (one ~3k-character C14N blob) instead of readable multi-line XML diffs. Official/Converted normalized panes have the same compact form.

Operator asked for prettier XML and (later) a separate page + GitHub-style collapse around diffs. **This hotfix:** pretty-print only. Separate page + hunks deferred to evolve (`D-S065-scope=4`).

## Error logs

Staging browser probe (2026-08-11), stem `sigmet-A6-1a-TS`:

```
hasDetail: true
hasDiff: true
diffLines: 4
longestLine: 2955
firstDiffPreview: "-<iwxxm:SIGMET reportStatus=\"NORMAL\" xmlns:aixm=..."
```

## Investigation

| Time | Note |
|------|------|
| 2026-08-11 | Confirmed on staging Quality metrics → SIGMET unequal |
| 2026-08-11 | `c14nXml` serializes compact (no newlines); `qualityMetricsDisplayXml` returns that form |
| 2026-08-11 | `unifiedLineDiff` splits on `\n` → one mega-line per document peer |
| 2026-08-11 | `prettyPrintXml` already exists for workbench F10 preview |
| 2026-08-11 | Root cause: display/diff path uses compact C14N without pretty-print |

**Root cause:** Normalized panes and the unified diff feed compact C14N into a line-oriented diff, so humans see one long line.

## Repro test

| Path | Status |
|------|--------|
| `apps/frontend/src/utils/qualityMetricsDisplayXml.test.ts` | red → green (2026-08-11) |
| `tests/bugs/test_bug_2026_08_11_quality_metrics_diff_long_line.py` | red → green (2026-08-11) |

## Interview record

- Intent: `/14-hotfix` staging Quality metrics long-line diffs
- Scope: `D-S065-scope=4` — hotfix readability now; evolve later for separate page + GitHub hunks
- Products: all stems
- Page: keep inline detail for now
- AskQuestion tool unavailable — numbered options; user chose “Proceed with recommended”
- Repro/root-cause confirmation: waived by “Proceed with recommended” after staging probe + red tests

## Fix

`qualityMetricsDisplayXml` now returns `prettyPrintXml(c14nXml(xml))` so Official/Converted panes and the unified line diff operate on multi-line peers. Diff rows also use `whitespace-pre-wrap break-all` as a safety net for long attribute lines.

## Prevention & countermeasures

(pending Phase 5)

## Follow-up

Evolve deepen F7.q: dedicated detail route + GitHub-style expandable/collapsible unchanged context.

See `docs/sessions/S065-quality-metrics-diff-long-line/FOLLOWUP.md` for seed prompt and ACs.
