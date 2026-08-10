# 01-requirements — S061 / EV-052

**Status**: completed — `D-S061-01-ac=1` (continue after `D-S061-redis=1`; UI N/A)  
**Date**: 2026-08-09  
**Mode**: delta (deepen F29, F6, F21, F30, M5 + ADR-007 gates)  
**Issues**: [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950),
[#900](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/900),
epic [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841)

## Corpus

[Corpus: product §F29] [Corpus: product §F6] [Corpus: product §F21]
[Corpus: product §F30] [Corpus: product §M5] [Corpus: tests] [Corpus: adr/ADR-007]
[Corpus: adr/ADR-006] [Corpus: adr/ADR-031] [Corpus: tech-spec] [Corpus: deploy]
[Corpus: decisions]

## Standing doc deltas

| Doc | Change |
|-----|--------|
| `docs/feature-list.md` | EV-052 deepen blocks (F29/F6/F21/F30/M5) |
| `docs/test-plan.md` | TC-EV052-001..012; coverage + quality PR comment + Sentry/Redis/Orval |
| `docs/decisions/evolve-decisions.md` | Cycle EV-052 + AC table |
| `docs/decisions/requirements-decisions.md` | EV-052 section |
| `docs/dependency-inventory.md` | sentry-sdk, @sentry/react, redis/upstash client, orval or openapi-typescript |
| `docs/adr/ADR-006-*.md` | Amend: Sentry optional on DOKS (Developer free) |
| `docs/adr/ADR-031-*.md` or note | Amend: slowapi may use Redis/Upstash shared store |
| `docs/config-spec.md` / `docs/env-contract.md` | `SENTRY_DSN*`, `REDIS_URL` / Upstash keys (04 finalizes names) |
| `docs/deploy.md` | Secret stubs for staging/prod Sentry + Redis |

## Skipped (N/A this cycle)

- New operator UJ / H4–H5 (no product UI journeys; Orval is codegen)
- UI preview (`D-S061-ui-preview=3` N/A)
- New Fn id (deepen only)
- Paid Sentry Team / DO Managed Valkey

## Acceptance criteria (locked `D-S061-01-ac=1`)

| AC | Issue / slice | Criterion | TC |
|----|---------------|-----------|-----|
| AC1 | #950 | Inventory every coverage surface + current vs ≥95% target | TC-EV052-001 |
| AC2 | #950 | Every listed surface enforces ≥95% in CI (pytest fail_under / --cov-fail-under / Vitest thresholds); soft/deferred gates removed | TC-EV052-002 |
| AC3 | #950 | Suite green **with** gates — fill tests; no silent waive; intentional excludes documented | TC-EV052-003 |
| AC4 | Quality PR | On PR, CI posts/updates **second sticky** comment (marker ≠ EV-036) with quality-matrix + annex3/`iwxxm_us` golden outcome stats: match / soft-diff / fail / skip by product × profile | TC-EV052-004 |
| AC5 | Quality PR | Formatter/script unit-tested; comment idempotent (update same sticky) | TC-EV052-005 |
| AC6 | #900 Sentry | API + FE + worker initialize Sentry when DSN set; disabled when unset; Developer free tier documented | TC-EV052-006 |
| AC7 | #900 Redis | slowapi (public + dissemination + mass-ingest as applicable) uses **Upstash Redis** when `REDIS_URL` (or approved Upstash env) set; falls back in-memory with warning when unset (dev only) | TC-EV052-007 |
| AC8 | #900 Redis | Multi-replica shared-store behavior covered by unit/integration (fake Redis or fakeredis) | TC-EV052-008 |
| AC9 | #900 Orval | OpenAPI → typed FE client (Orval **or** openapi-typescript) generated; FE uses generated types for high-churn convert/validate paths (or thin wrapper); CI drift check or committed artifact policy | TC-EV052-009 |
| AC10 | Docs | feature-list / test-plan / env-contract / deploy / dependency-inventory / ADR-006+031 notes accurate | TC-EV052-010 |
| AC11 | Infra | Free-tier limits recorded; no new DOKS Redis Deployment; Upstash + Sentry secrets documented | TC-EV052-011 |
| AC12 | CI | PR CI green with coverage gates + quality comment job + unit tests for new scripts | TC-EV052-012 |

## Defaults (Phase 0)

| ID | Locked |
|----|--------|
| D-S061-redis | **1** — Upstash Redis free (no new DOKS Redis service) |
| D-S061-comment | Second sticky (separate from coverage) |
| D-S061-quality-source | Quality-matrix smoke/full pack + annex3/`iwxxm_us` goldens |
| D-S061-orval | Orval **or** openapi-typescript — pick in 04 |
| D-S061-preset | Standard; skip 03/06/10/12/13 unless live Redis proof needed |
| D-S061-ui-preview | N/A |

## Next

**02-verify-plan** (Gate A).
