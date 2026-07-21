# 04-tech-plan — S019 / EV-014 (delta)

**Date**: 2026-07-21  
**Mode**: delta / evolve  
**Status**: in_progress — Batch 1 locked (Q32=A); Batch 2 pending

## Inputs

- Phase A passed (Q31=A); deferred_from_01 tech intake
- PR [#753](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/753)

## Batch 1 — Architecture (LOCKED — Q32=A)

| ID | Answer | Decision |
|----|--------|----------|
| E14-01 | B | `packages/dissemination` + thin backend routers |
| E14-02 | A | SQLAlchemy 2 async + dialect drivers; versioned writer-contract DDL |
| E14-03 | A | `POST /api/v1/dissemination/preflight` + `…/send` |
| E14-04 | B | wis2box = Docker Compose / CI harness (not Render web service) |
| E14-05 | A | EDIS via `aiosmtplib`; F19 adapters on same sink interface |

**ADR**: [ADR-030](../../../adr/ADR-030-dissemination-package-architecture.md) Accepted

## Artifacts updated (Batch 1)

| Document | Delta |
|----------|-------|
| ADR-030 | Package + sink architecture |
| `docs/spec.md` | Component Overview + F16–F19 ADR cite |
| `docs/api-contract.md` | Planned dissemination routes |
| `docs/dependency-inventory.md` | Planned package + deps |
| plan-adherence / template-conformance | `packages/dissemination` |
| evolve-decisions EV-014 | Batch 1 table |

## Pending batches

| Batch | Topics |
|-------|--------|
| 2 | Deploy / harness / allowlist env / test strategy / FE connectivity |
| 3 | Exact driver pins + msgspec vs pydantic on dissemination routes + milestone cut |
| Plan approve | execution-plan.md tasks |

## Next

Batch 2 written interview → then draft `execution-plan.md`.
