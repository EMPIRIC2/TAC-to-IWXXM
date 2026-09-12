# Evolve summary — S071 / EV-061

> Closed: 2026-08-20 · `D-S071-13` · `D-S071-close`  
> Product: [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016) → `stage` @ `86867a11`  
> Docs: [#1018](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1018) → `stage`  
> Staging CD: [32398410519](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32398410519)  
> Standing report: [docs/evolve-report-EV-061.md](../../../evolve-report-EV-061.md)

## Shipped

| Ticket | Outcome |
|--------|---------|
| #1011 | Live bulletin multipart field `file` → `files` |
| #1012 | AHL bulletin decode + convert end-to-end |
| #1010 | IWXXM validate readable item-by-item decode |
| #1013 | Product Type + Profile top bars (polish / no wrap) |
| #1014 | Lint + validation catalog tab with working source links |
| #1015 | Stricter stage→main CI gate (lint/typecheck/E2E Full) |
| #1009 | Epic closed on S071 closeout |

## Verify

| Stage | Verdict |
|-------|---------|
| Spec→Build | open (`D-S071-spec-build=1a`) |
| 07–11 | PASS (M1–M6; 11 user approve UJ-064..068) |
| 12-verify-deploy | PASS checklist + merge (`D-S071-12-merge=1`) |
| 13-deploy-smoke | PASS (`D-S071-13`) — H0c–H5 + live UJ-064..068 6/6 |

## Deferred

- Promote `stage`→`main` (admin rulesets + separate AskQuestion)
- Catalog source deepen / category sort-filter → [#1017](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1017)

## Corpus

[Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F9] [Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34] [Corpus: journeys] [Corpus: tests] [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: decisions §EV-061]
