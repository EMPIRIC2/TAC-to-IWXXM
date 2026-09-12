# Build Plan Card

> Session: S056-m0-stabilize-operator-trust | Cycle: EV-047 | Updated: 2026-08-08

## Goal

Slim husky to lint + fast units; hard-fail converter perf regressions vs **committed
CI baselines**; ship operator one-pager + handbook + Help link.

## Out of scope

AMS abstract (#958); converter micro-opts; requiring Converter perf ruleset **before**
the CI job exists; 12/13 deploy unless 11 needs it.

## Active milestone

**M1 — Converter perf baselines + hard harness** (first: establish baseline to compare against)

## Task batch (next 07)

| ID | Title | Notes |
|----|-------|-------|
| T1.1 | Contract tests for baseline schema + hard gate | red first |
| T1.2 | Harness + `make perf-converter-baseline` | |
| T1.3 | **Commit CI-class `converter_pr.yaml` baselines** | user priority |
| T1.4 | `ci-cd.yml` job `Converter perf (tac2iwxxm)` | |
| T1.5 | Apply rulesets including Converter perf | after job on branch |

Then M2 (husky) ∥ M3 (docs/Help).

## Locked tech (pending `D-S056-04-plan`)

- Baseline file: `tests/perf/baselines/converter_pr.yaml`
- Ceiling: `max(p95×1.20, p95+50µs)`; convert-only; METAR/SPECI/TAF + thin SIGMET
- Husky A + `make test-unit-fast` = workspace + tac2iwxxm units
- Ruleset defer until job ships (`D-S056-ruleset-defer=2`)

## Risks

- CI runner noise → floor + retry policy  
- Ruleset admin apply still needed at T1.5  
- Help placement in existing shell  

## Next

Approve execution plan → **05-verify-tech** (or skip-light) → **07-build** M1.
