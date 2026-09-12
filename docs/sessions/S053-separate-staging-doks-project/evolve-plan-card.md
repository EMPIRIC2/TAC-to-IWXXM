# Evolve Plan Card

> Cycle: EV-044 | Session: S053-separate-staging-doks-project | Updated: 2026-08-08

## Goal

Put staging on its own DOKS + Postgres under DO Project **Staging TAC-to-IWXXM**, keep prod
on **TAC-to-IWXXM**, preserve promote-from-stage CD.

## Features

- F30 — Platform independence (deepen: dual DO projects / dual DOKS) — [Corpus: product §F30]

## In / out of scope

- In: staging DOKS + PG under Staging project; CD kubeconfig split; DNS to new LB; ADR-034 amend; teardown shared-ns staging
- Out: UI features; App Platform; promote-policy change; Render

## Preset + routing

- Preset: **Standard**
- Stages (ordered): `00 → 16 → 01 → 02 → 03 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`
- Skip: `06`

## Next child stage

`01-requirements` — delta F30 ACs + ADR-034 amend draft for separate staging cluster/DB

## Risks / open decisions

- Porkbun DNS cutover to new LB (operator)
- GH admin Environments / dual `KUBE_CONFIG` secrets (may 403)
- Cost: ~2× cheapest DOKS + cheapest PG for staging
- Data migration from logical `metar_iwxxm_staging` → new DBaaS (schema via Alembic; optional data copy)
