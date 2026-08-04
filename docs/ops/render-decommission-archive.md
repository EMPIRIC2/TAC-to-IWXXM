# Render decommission archive (TC-F30-005 / T6.5)

> **Status**: **suspended** 2026-08-03 under **`D-S038-t65-waive`** (7-day soak waived; day 0/7)  
> **Session**: S038-platform-independence-842 / EV-031  
> **Primary compute**: DOKS LB `168.144.12.70` + Host-header placeholders (`D-S038-t63-waive`)  
> **Do not** resume these services without an explicit evolve/hotfix decision.

## Suspended production services

| Name | Service ID | Type | Historical public URL | Suspended |
|------|------------|------|-----------------------|-----------|
| `metar-to-iwxxm-api` | `srv-d69v688gjchc73cn9kg0` | web_service | `https://metar-to-iwxxm-api.onrender.com` | 2026-08-03 |
| `metar-to-iwxxm-frontend-v4-web` | `srv-d6cvj2i4d50c73aelapg` | web_service | `https://metar-to-iwxxm-frontend-v4-web.onrender.com` | 2026-08-03 |
| `metar-to-iwxxm-worker` | `srv-d99u0i8k1i2s73eq5oqg` | background_worker | (no public URL) | 2026-08-03 |

Post-suspend probe: API `/health` → **503**. DOKS Host-header `/health` → **200**.

## Historical LIVE_* (Render)

```bash
# ARCHIVED — do not use for make test-live* after T6.5
# LIVE_API_URL=https://metar-to-iwxxm-api.onrender.com
# LIVE_FRONTEND_URL=https://metar-to-iwxxm-frontend-v4-web.onrender.com
```

Canonical live harness (provisional DOKS):

```bash
# /etc/hosts → 168.144.12.70 api… / app… placeholders
export LIVE_API_URL=http://api.doks.placeholder.metar-iwxxm.local
export LIVE_FRONTEND_URL=http://app.doks.placeholder.metar-iwxxm.local
```

See [doks-cutover-soak-checklist.md](doks-cutover-soak-checklist.md) and `config/prod.json` `liveE2e.*`.

## Already-suspended (pre-T6.5)

| Name | Service ID | Notes |
|------|------------|-------|
| `metar-to-iwxxm-frontend` / `-v2` / `-v3` / `-v4` | various | Legacy static sites |
| `metar-to-iwxxm-frontend-web` | `srv-d6cvij15pdvs739mctl0` | Superseded by v4-web |
| `metar-to-iwxxm-grafana` / `-prometheus` / `-loki` | various | Observability stack (ADR-006 out of Blueprint) |

## CI / Blueprint

- `.github/workflows/ci-cd.yml` **Deploy** job pushes GHCR images only; **Render deploy hooks retired** (T6.5).
- `render.yaml` retained as historical Blueprint reference until a later cleanup ticket deletes it.
- Resume path (emergency only): Render Dashboard or `POST /v1/services/{id}/resume` with `RENDER_API_KEY`.

## Residual (not T6.5)

- Real public DNS + HTTPS (lift `D-S038-t63-waive`)
- GHCR `write:packages` republish of `backend|frontend:ev031-doks`; drop ConfigMap sslmode mount + FE hot-copy
- Optional hard-delete of suspended Render services after operator confirmation
