# Deploy Checklist — S038 / EV-031 (Stage 12)

> Generated: 2026-08-03  
> Status: **awaiting sign-off**  
> Deployment plan: [docs/deploy.md](../../../deploy.md) · [deploy-report.md](deploy-report.md)  
> Session: S038-platform-independence-842 · Evolve: EV-031  
> Branch: `evolve/EV-031-platform-independence-842` · tip `4caaae1b`  
> Lock: DOKS primary (`D-S038-doks-depth=3`); provisional DNS (`D-S038-t63-waive`); Render suspended (`D-S038-t65-waive`)

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| Product DB | DO Postgres via `DATABASE_URL` | Already on DOKS; Alembic `upgrade head` in release path |
| Auth | Supabase Auth JWKS-only | No Auth deployable change |
| API / FE / worker | DOKS namespace `metar-iwxxm` | Primary compute — Host-header provisional |
| F31 hybrid sessions | Guest local + login → DO sessions | FE image / ConfigMap runtime (hot-copy interim) |
| Render | Suspended | Keep suspended; do not revive for product path |
| Secrets | `DATABASE_URL`, Auth JWKS/url, CORS | Documented in deploy.md + DOKS ConfigMaps |

## Pre-Deploy

- [x] Configuration complete — DOKS kustomize + `config/prod.json` provisional placeholders
- [x] Secrets documented — `DATABASE_URL` + Auth JWKS; no product Supabase DB
- [x] Data assets — vendor schemas in image; N/A weights
- [x] Resource allocation — cheapest DOKS profile (provision report)
- [x] Rollback plan — reviewed below (awaiting user approve)
- [x] H0c CORS — `pytest tests/unit/test_cors_policy.py` **6/6 PASS** (2026-08-03)
- [x] Frontend runtime ↔ API matrix — provisional Host + `config.json` `api.baseUrl` (T7.2 H5)
- [x] `METAR_CORS_ORIGINS` / ConfigMap CORS — DOKS FE placeholder + LB IP
- [x] Post-deploy H4–H5 command — `make test-live-connectivity-doks-provisional` / `verify_connectivity.sh`
- [x] Connectivity scripts present — `scripts/deploy/verify_connectivity.sh`, `tests/smoke/test_staging_connectivity.py`
- [x] Implementation approved — 11-verify-impl (`D-S038-11` = 1)

## Agent checks (12)

| Agent | Result |
|-------|--------|
| 1 Configuration | **PASS** — placeholders + DOKS manifests pinned; real DNS residual tracked |
| 2 Secrets | **PASS** — Auth + `DATABASE_URL` on DOKS; Render product secrets retired |
| 3 Data / volumes | **N/A** — Postgres managed; no Modal volumes |
| 4 Resources | **PASS** — DOKS cheapest profile per provision report |
| 5 Template deploy | **PASS (delta)** — GHCR + DOKS path; Render hooks retired |
| 6 Browser connectivity | **PASS (provisional)** — H0c 6/6; T7.2 H4–H5 Host-header |

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Image / GHCR publish blocked | Interim ConfigMap + FE hot-copy; republish when `write:packages` available | proposed |
| 2 | Placeholder DNS / HTTP only | Host-header smoke + `D-S038-t63-waive`; lift when real DNS lands | proposed |
| 3 | CORS dual-host confusion | Document DOKS primary; Render FE/API suspended | proposed |
| 4 | Alembic miss on rollout | Release job / init: `python -m alembic upgrade head` (idempotent) | proposed |
| 5 | Session / sslmode drift | ConfigMap `sslmode=require` until `backend:ev031-doks` republish | proposed |
| 6 | Accidental Render revive | T6.5 archive + keep suspended until DNS cutover complete | proposed |

## Rollback

1. **Compute**: Re-point traffic / Ingress away from DOKS only after real DNS exists; until then keep Host-header provisional path.
2. **Images**: Pin prior GHCR tags for API/FE/worker; `kubectl rollout undo` in `metar-iwxxm`.
3. **DB**: Do **not** drop DO Postgres; reverse only app image / ConfigMap if needed. Migrations are forward-only (Alembic).
4. **Render**: Remains suspended — rollback is **not** “unsuspend Render as primary” without an explicit decision (would undo F30 AC5).
5. **Verify after rollback**: `bash scripts/deploy/doks_host_header_smoke.sh` + `make test-live-connectivity-doks-provisional`.

Last known good provisional cutover evidence: T6.4 **5/5**, T7.1 **13/13**, T7.2 H4–H5 **PASS**, tip lineage through `4caaae1b`.

## Smoke order (13)

1. Confirm DOKS LB `168.144.12.70` + Host headers still healthy.
2. Re-run `doks_host_header_smoke.sh` + provisional H4–H5.
3. Optional: Playwright provisional pack / topology live tests.
4. Record residuals (real DNS, GHCR republish) in deploy-report / evolve-summary.
5. Do **not** require public HTTPS until `D-S038-t63-waive` lifted.

## Sign-Off (gate)

- [x] User approved implementation (11-verify-impl / `D-S038-11`)
- [ ] User approved failure mitigations
- [ ] User approved rollback plan
- [ ] Ready for **13-deploy-smoke**
