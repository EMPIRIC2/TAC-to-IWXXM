# 01-requirements report — S067 / EV-057

> **Status**: completed · **Date**: 2026-08-15  
> **Mode**: delta · **Preset**: Standard  
> **Corpus**: [Corpus: product §F7] [Corpus: product §F30] [Corpus: product §F2]
> [Corpus: product §F4] [Corpus: deploy] [Corpus: journeys] [Corpus: tests]
> [Corpus: system-spec] [Corpus: decisions §EV-057]

## Startup

| ID | Choice |
|----|--------|
| D-S067-01-goal | **1a** — lock AC + journeys + tests + deploy for all three |
| D-S067-01-manifest | **1a** — feature-list, journeys, test-plan, deploy, light spec; skip README/deps |
| D-S067-01-ui | **1a** — docs only; honor remind at 11 |
| D-S067-01-delta | **1a** — no scope change from S067 open |
| D-S067-01-ac | **1a** — approve drafted AC |
| D-S067-01-api | **1a** — skip api-contract unless 04 finds wire gap |
| D-S067-01-spec | **1a** — light spec.md note only |

## Document deltas written

| Document | Delta |
|----------|-------|
| `docs/feature-list.md` | F7.r (#903), F7.s (#838), F30 deepen (#948) + AC |
| `docs/user-journeys.md` | UJ-057, UJ-058, UJ-OPS-002 |
| `docs/test-plan.md` | TC-EV057-948/903/838 mapping |
| `docs/deploy.md` | Apex redirect section |
| `docs/spec.md` | F7.r / F7.s notes under frontend |
| `docs/decisions/requirements-decisions.md` | EV-057 table |
| `docs/decisions/evolve-decisions.md` | AC lock |

## Open for 04

- Exact soft accumulate cap number (from existing workbench/F33 caps)
- Concrete Ingress/Service name for #948 after live DNS/ingress read
- Confirm `POST /api/v1/validate` covers paste/upload payloads (re-open api-contract only on gap)

## Next

**02-verify-plan** (Gate A) → then **04-tech-plan**.
