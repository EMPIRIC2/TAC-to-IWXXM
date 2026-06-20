# ADR-006: Render Topology Simplification

## Status: Accepted

## Context

Current production uses three application web services (API, auth, frontend nginx) plus
Loki/Prometheus/Grafana private services. Post-migration spec (ADR-002, deploy.md) targets two
deployables: unified API and static frontend. Observability pservs add cost and complexity
without being required for migration validation.

## Decision

1. **Frontend**: Deploy as **Render Static Site** (Vite build → CDN), not Docker/nginx web service.
2. **API**: Single Docker web service including packages/auth (no separate auth service).
3. **Observability**: **Remove** Loki, Prometheus, and Grafana from `render.yaml`; rely on Render built-in logs.
4. **URLs**: Keep existing onrender.com hostnames; rename env vars only (`VITE_API_BASE_URL`, `METAR_CORS_ORIGINS`).
5. **Auth**: Set `DISABLE_AUTH=false` in production as part of migration (Supabase credentials required on Render).

## Consequences

- Frontend deploy model changes from container to static — update CI build/publish steps.
- `render.yaml` shrinks significantly; observability dashboards in Grafana are lost unless re-added later.
- Auth enablement requires Supabase secrets verified before production deploy.
- H4/H5 connectivity tests use unchanged staging URLs with new env var names.

## Alternatives Considered

- **Keep Docker/nginx frontend**: Rejected — static site is simpler, cheaper, and matches deploy.md target.
- **Keep observability pservs**: Rejected — out of migration scope; adds pserv wiring maintenance.
- **Custom domains**: Deferred — user chose to keep onrender.com URLs for now.
- **Keep DISABLE_AUTH=true**: Rejected — user chose to enable production auth in migration.
