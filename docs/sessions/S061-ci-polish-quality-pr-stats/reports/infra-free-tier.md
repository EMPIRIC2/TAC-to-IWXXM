# Infra / free-tier report — EV-052 / S061

> Checked 2026-08-09. Cite vendor pages at implement time (tiers change).

## Current stack (reuse)

| Piece | Today | Reuse? |
|-------|-------|--------|
| DOKS workloads | `metar-api`, `metar-frontend`, `metar-worker` (+ alembic Job) | Yes — no Redis Deployment in `deploy/doks/base` |
| Rate limits | `slowapi` **in-memory** (`abuse_controls.create_limiter`) | Partial — works single-replica; **not cluster-correct** |
| Dissemination limiter | In-process `DisseminationRateLimiter` | Same multi-replica caveat |
| Observability | DOKS / platform logs; ADR-006 removed Loki/Prom/Grafana from Render | Sentry is additive SaaS |
| Coverage PR comment | EV-036 `coverage-pr-comment` + `format_coverage_pr_comment.py` | Pattern reuse for quality sticky comment #2 |
| OpenAPI | FastAPI `/openapi.json` | Source for Orval / openapi-typescript |

## Free-tier verification

### Sentry — Developer plan (**$0**)

Source: [sentry.io/pricing](https://sentry.io/pricing/) (fetched 2026-08-09)

| Limit | Developer (free) |
|-------|------------------|
| Price | $0 |
| Users | **1** |
| Errors | **5k / month** |
| Tracing spans | **5M / month** |
| Session Replay | **50 / month** |
| Logs | **5GB** |
| Attachments | **1GB** |

**Infra changes (no new K8s service):**

1. Create Sentry org/projects (api, frontend, worker) on Developer plan.
2. Store DSNs in DOKS secrets (staging + prod): e.g. `SENTRY_DSN`, `VITE_SENTRY_DSN` /
   runtime `/config.json` key — exact names in 04 / env-contract.
3. SDK deps: `sentry-sdk[fastapi]` (API+worker), `@sentry/react` (FE).
4. Optional: release/environment tags = `staging` | `prod`; sample rates to stay under 5k.

**Not free:** Team ~$26/mo (multi-user, higher quotas). Stay on Developer unless quota fails.

### Redis for distributed rate limits

**Problem if we add no shared store:** with ≥2 API replicas on DOKS, in-memory slowapi
allows roughly `N × limit` per IP. That is a **significant correctness gap** for public
abuse controls (F21 / ADR-031) — raised here per intake.

| Option | Cost | New DOKS service? | Notes |
|--------|------|-------------------|-------|
| **A. Upstash Redis free** (recommended) | **$0** — 256 MB, **500k commands/mo**, 10 GB bandwidth ([Upstash Redis pricing](https://upstash.com/pricing/redis)) | **No** — external TLS endpoint | Env `REDIS_URL` / Upstash REST; slowapi Redis storage; egress allowlist if needed |
| B. In-cluster Redis/Valkey on existing nodes | Node RAM/CPU only (no Managed Valkey $) | **Yes** — new Deployment+Service+PVC | More ops; fits “reuse cluster” but is still a new service |
| C. DO Managed Valkey | ~$15+/mo | Managed | Reject unless free path fails |
| D. Keep in-memory only | $0 | No | **Significant issue** — multi-replica under-enforcement |

Rough free-tier headroom (Upstash): public limit 60/min/IP → on the order of tens of
thousands of limited requests/day before command pressure; rate-limit keys are tiny vs 256 MB.

### Orval / openapi-typescript

| Item | Cost | Infra |
|------|------|-------|
| Orval or `openapi-typescript` + TanStack Query wiring | $0 OSS | **None** — CI/local codegen; commit or generate-in-CI policy in 04 |

## Summary recommendation

1. **Sentry Developer** — ship; secrets only; amend ADR-006 observability note.
2. **Rate limits** — prefer **Upstash free** (no new K8s Service). If policy forbids
   external Redis, choose in-cluster Redis and accept a new DOKS service.
3. **Orval/openapi-typescript** — no infra.
4. **Quality PR comment** — extend CI only (reuse github-script sticky pattern).

## Decision needed

`D-S061-redis` — A Upstash free / B in-cluster / D keep in-memory (not recommended).
