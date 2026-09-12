# Session brief — S061-ci-polish-quality-pr-stats

> **Cycle**: EV-052 · **Type**: feature · **Opened**: 2026-08-09  
> **Branch**: `evolve/EV-052-ci-polish-quality-pr-stats` (base `stage@80197a58`)  
> **Orchestrator**: 16-evolve  
> **Corpus**: [Corpus: product §F6] [Corpus: product §F29] [Corpus: product §F21]
> [Corpus: product §M5] [Corpus: product §F30] [Corpus: tests] [Corpus: adr/ADR-007]
> [Corpus: adr/ADR-006] [Corpus: adr/ADR-031] [Corpus: tech-spec] [Corpus: deploy]

## Goal

CI polish: restore universal **≥95% coverage gates** (#950); ship a **second sticky PR
comment** with golden/quality-matrix outcome stats by product × profile; implement free-tier
**Sentry** + distributed **rate-limit store** + **OpenAPI→typed FE client** (#900 2–4).

## Intent (locked intake — D-S061-intake)

| # | Choice |
|---|--------|
| Open | 1 — S061 / EV-052 for A + #950 + #900 |
| Quality comment | 1 — quality-matrix + annex3/`iwxxm_us` golden packs; match / soft-diff / fail / skip by product × profile |
| Comment UX | 1 — **second** sticky comment (separate from EV-036 coverage) |
| #900 | 2–4 — implement free Sentry + Redis-backed limits + Orval/openapi-typescript |
| Preset | 1 — **Standard** |
| UI preview | N/A — CI / infra / codegen (no operator UI redesign) |
| Infra | Reuse existing where possible; raise if skipping a new shared rate-limit store is a significant issue |

## Out of scope

- Mutation testing (#874), Schemathesis (#727)
- In-app operator UI for quality metrics (#836) — CI PR comment only this cycle
- Paid Sentry Team / DO Managed Valkey unless free path fails
- Clerk/Auth0, Next.js, SQLModel migration (#900 don'ts)
- `stage`→`main` promote / tag-driven prod cutover (separate)
- Parked S058 / #958 AMS abstract

## Features (proposed — confirm in Plan)

- Deepen **F29** — quality matrices → PR sticky summary comment
- Deepen **F6** — M-golden / profile outcome aggregation for CI
- Deepen **F21** / ADR-031 — slowapi storage → shared Redis-compatible backend
- Deepen **F30** / ADR-006 amend — Sentry on API + FE + worker (DOKS secrets)
- Deepen **M5** — Orval or openapi-typescript FE client from OpenAPI
- **#950** — ADR-007 / test-plan 95% gate restoration (all packages/apps)

## Related issues

- [#950](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/950) — coverage gates
- [#900](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/900) — stack follow-ups (implement free path)
- Epic [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841) — CI / DX hardening (parent)

## UI preview

N/A — no browser UI product work this session (Orval is build-time codegen only).
