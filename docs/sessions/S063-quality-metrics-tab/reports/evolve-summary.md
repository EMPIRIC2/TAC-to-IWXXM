# Evolve summary — EV-054 / S063 (Quality metrics tab)

> **Status**: **completed** (`D-S063-13=1` / `D-S063-close=1`) — 2026-08-11  
> **PR**: [#977](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/977) **MERGED** → `stage` @ `4fd51e39`  
> **Issue**: [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836) **CLOSED**  
> **Promote**: **no** — stay on stage (`D-S063-13=1`)  
> **Corpus**: [Corpus: product §F7] [Corpus: journeys] [Corpus: tests] [Corpus: api]
> [Corpus: decisions §EV-054]

## Shipped

- Operator **Quality metrics** primary shell tab (F7.q / F7 deepen)
- Public `GET /api/v1/quality-metrics` + `/{stem}` (precomputed corpus blob)
- Unified XML diff + residuals / lint / validate panels
- UJ-056 Playwright + live staging smoke
- Stage CD green: [31453072506](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31453072506)

## Follow-ups (filed at close — Ready)

| Issue | Topic |
|-------|--------|
| [#979](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/979) | Investigate `SCHEMA_IMPORT_WARNING` for 2025-2 |
| [#980](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/980) | Investigate `SCHEMATRON_SKIPPED` for 2025-2 (xslt2) |
| [#981](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/981) | Optional propagate residuals into remarks |
| [#982](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/982) | Whitespace-normalize official XML for truer diffs |
| [#983](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/983) | Selectable side-by-side vs inline XML diff |

## Decisions (close)

| ID | Choice |
|----|--------|
| D-S063-13 | **1** — Approve smoke; close EV-054 / S063; **stay on stage** (no promote) |
| D-S063-close | **1** — Close #836; clear `active_session`; follow-ups #979–#983 |
