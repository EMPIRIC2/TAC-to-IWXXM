# 04-tech-plan — S019 / EV-014 (delta)

**Date**: 2026-07-21  
**Mode**: delta / evolve  
**Status**: in_progress — Batch 1–2 locked; execution-plan pending approval (Q34)

## Inputs

- Phase A passed (Q31=A)
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

## Batch 2 — Deploy / test / integration (LOCKED — all A / Q33)

| ID | Answer | Decision |
|----|--------|----------|
| E14-06 | A | SQL Server via `aioodbc` + ODBC docs |
| E14-07 | A | msgspec on dissemination routes |
| E14-08 | A | `DISSEMINATION_EGRESS_ALLOWLIST` env-contract + Render; empty fail-closed |
| E14-09 | A | Unit + Compose/Testcontainers + mocks; live BYOC = close gate |
| E14-10 | A | Ship FE drawer this cycle; H4–H5 required |

## Artifacts

| Document | Delta |
|----------|-------|
| ADR-030 | Package + sink architecture |
| execution-plan.md | M1–M6 + T0.1 (32 tasks) — **pending Q34** |
| env-contract / config-spec / deploy | Allowlist |
| api-contract | msgspec encode locked |
| dependency-inventory | aioodbc / pin notes |
| msgspec-http-boundary | dissemination routes |

## Next

**Q34** — approve execution plan → complete 04 → 05-verify-tech.
