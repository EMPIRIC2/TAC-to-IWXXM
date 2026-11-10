# Integration contract

> Index: [README.md](README.md) 
> Last updated: 2026-11-10

This document states how external systems connect to TAC to IWXXM.
HTTP field shapes remain in [api-contract.md](api-contract.md) and
[api/openapi.json](../api/openapi.json).

## Auth

| Rule | Detail |
|------|--------|
| Provider | Supabase Auth issues JWTs |
| API role | `packages/auth` verifies JWTs and serves `/auth/*` on the API |
| Public routes | Convert, lint, validate, decode, preview, and disseminate stay public |
| Protected routes | Long-term work sessions require a Bearer JWT |

## Product database

| Rule | Detail |
|------|--------|
| Engine | DigitalOcean Postgres |
| Access | `DATABASE_URL` from API and worker |
| Not used | Supabase product PostgREST or product database |

## Airport and map data

| Rule | Detail |
|------|--------|
| Purpose | Station and airspace context for convert and Decode visuals |
| Constraint | Browser keys and provider attribution must follow UI style and privacy rules |

## Dissemination sinks

| Rule | Detail |
|------|--------|
| Pattern | Backend-mediated bring-your-own-credentials |
| Secrets | Memory-only for one send |
| Allowlist | `DISSEMINATION_EGRESS_ALLOWLIST` required |
| Pathways | Multi-database URI, WIS2, EDIS, and AMHS/SWIM/AFS |

## Frontend to API

| Rule | Detail |
|------|--------|
| Discovery | Runtime `/config.json` or build-time API base URL |
| CORS | API `METAR_CORS_ORIGINS` / profile `corsOrigins` must list the UI origin |

## Local feeder

Historical notes may exist under local `docs/integration/`. Prefer this contract
and OpenAPI for new work.
