# 04-tech-plan — S019 / EV-014 (delta)

**Date**: 2026-07-21  
**Mode**: delta / evolve  
**Status**: **completed** — Q34=A plan approved; handoff for next chat

## Inputs

- Phase A passed (Q31=A)
- PR [#753](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/753) → retarget/`main` merge for session handoff

## Batch 1 — Architecture (LOCKED — Q32=A)

| ID | Answer | Decision |
|----|--------|----------|
| E14-01 | B | `packages/dissemination` + thin backend routers |
| E14-02 | A | SQLAlchemy 2 async + dialect drivers; versioned writer-contract DDL |
| E14-03 | A | `POST /api/v1/dissemination/preflight` + `…/send` |
| E14-04 | B | wis2box = Docker Compose / CI harness (not Render web service) |
| E14-05 | A | EDIS via `aiosmtplib`; F19 adapters on same sink interface |

**ADR**: [ADR-030](../../../adr/ADR-030-dissemination-package-architecture.md) Accepted

## Batch 2 — Deploy / test / integration (LOCKED — all A)

| ID | Answer | Decision |
|----|--------|----------|
| E14-06 | A | SQL Server via `aioodbc` + ODBC docs |
| E14-07 | A | msgspec on dissemination routes |
| E14-08 | A | `DISSEMINATION_EGRESS_ALLOWLIST` env-contract + Render; empty fail-closed |
| E14-09 | A | Unit + Compose/Testcontainers + mocks; live BYOC = close gate |
| E14-10 | A | Ship FE drawer this cycle; H4–H5 required |

## Plan approval

| ID | Decision |
|----|----------|
| Q34=A | Approve [execution-plan.md](execution-plan.md) — M1–M6 + T0.1 (32 tasks) |

## Artifacts

| Document | Status |
|----------|--------|
| ADR-030 | Accepted |
| execution-plan.md | **Approved** |
| env-contract / config-spec / deploy | Allowlist documented |
| api-contract | Planned dissemination + msgspec |
| dependency-inventory | Planned package deps |

## Handoff (next chat)

1. Resume **S019 / EV-014** on `main` after #753 merge (or branch tip).
2. Run **05-verify-tech** (delta audit of execution plan + corpus).
3. Then **06-tech-tooling** (T0.1) → Phase B checkpoint → **07-build** M1 T1.1.
4. Close gate unchanged: live BYOC Postgres + WIS2 + EDIS before cycle close.
