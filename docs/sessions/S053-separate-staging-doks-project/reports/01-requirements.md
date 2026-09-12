# 01-requirements — S053 / EV-044 (delta)

**Status**: complete (delta)  
**Date**: 2026-08-08  
**UI preview**: N/A — no product UI

## Corpus cites

[Corpus: product §F30] [Corpus: deploy] [Corpus: tests] [Corpus: adr/ADR-034]
[Corpus: tech-spec] [docs/decisions/evolve-decisions.md §Cycle EV-044]

## Locked intake

| ID | Choice |
|----|--------|
| D-S053-open | Standard S053/EV-044 |
| D-S053-db | New cheapest managed PG under Staging project |
| D-S053-size | 1× `s-2vcpu-4gb` staging DOKS |
| D-S053-teardown | Tear down shared-cluster staging ns after cutover |

## Artifacts updated

| Path | Change |
|------|--------|
| `docs/adr/ADR-034-*.md` | Dual-cluster + dual DO Project amend |
| `docs/feature-list.md` | F30 deepen EV-044 + AC13 |
| `docs/deploy.md` | Topology / CD / secrets for dual cluster |
| `docs/test-plan.md` | TC-F30-008′ / 009 / 010 / **013** |
| `docs/ops/doks-staging-dns-runbook.md` | Staging LB IP + DO Projects |
| `.cursor/rules/optional/doks-promote-from-stage.mdc` | Dual cluster table |
| `docs/decisions/evolve-decisions.md` | §Cycle EV-044 |

## Gate A ready when

02-verify-plan confirms F30 deepen ACs + ADR-034 amend + evolve-decisions §EV-044 consistency.
