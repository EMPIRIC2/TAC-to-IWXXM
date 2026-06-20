# Render Observability Setup (Grafana + Prometheus + Loki)

This guide configures observability for the live Render environment using:

- `metar-to-iwxxm-prometheus`
- `metar-to-iwxxm-loki`
- `metar-to-iwxxm-grafana`

The Render blueprint definitions are in `render.yaml`.

## 1) Apply blueprint changes

1. Push the updated repository.
2. In Render, re-sync the Blueprint for this repo/branch.
3. Confirm the new services are created:
   - `metar-to-iwxxm-prometheus` (private)
   - `metar-to-iwxxm-loki` (private)
   - `metar-to-iwxxm-grafana` (web)

## 2) Secret mapping (`.env` -> Render)

Use values from local `.env` only as source material. Do not commit secrets.

### Existing app secrets

- Backend (`metar-to-iwxxm-api`):
  - `DATABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `OPENAIP_API_KEY`
- Auth (`metar-to-iwxxm-auth-v2`):
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`

### New observability secrets

- Backend + Auth:
  - `LOKI_USERNAME`
  - `LOKI_PASSWORD`
- Grafana:
  - `GF_SECURITY_ADMIN_USER`
  - `GF_SECURITY_ADMIN_PASSWORD`

### CI pipeline secrets (GitHub Actions)

- Existing load test secrets:
  - `LOAD_TEST_TARGET_URL`
  - `LOAD_TEST_AUTH_URL`
  - `LOAD_TEST_EMAIL`
  - `LOAD_TEST_PASSWORD`
- New optional Loki event shipping:
  - `LOAD_TEST_LOKI_PUSH_URL`
  - `LOAD_TEST_LOKI_USERNAME`
  - `LOAD_TEST_LOKI_PASSWORD`

## 3) Metrics endpoints

Metrics are exposed by app services:

- Backend: `/metrics` on `metar-to-iwxxm-api`
- Auth: `/metrics` on `metar-to-iwxxm-auth-v2`

Prometheus scrapes both services from the Render private network.

## 4) Translation success metrics

The backend now emits conversion metrics from the statistics logging flow:

- `metar_conversions_total{status, iwxxm_version, icao_region}`
- `metar_conversion_duration_seconds{status, iwxxm_version, icao_region}`

Recommended SLO query examples:

- Success rate (15m):
  - `sum(rate(metar_conversions_total{status="success"}[15m])) / sum(rate(metar_conversions_total[15m]))`
- P95 duration (5m):
  - `histogram_quantile(0.95, sum by (le) (rate(metar_conversion_duration_seconds_bucket[5m])))`

## 5) Log ingestion

Backend and auth services push structured JSON logs to Loki via:

- `LOKI_PUSH_URL=http://metar-to-iwxxm-loki:3100/loki/api/v1/push`

Frontend remains on Render-native logs in phase 1.

## 6) Dashboards and provisioning

Repository assets:

- `monitoring/grafana-dashboard.json`
- `monitoring/grafana/provisioning/datasources/datasources.yml`
- `monitoring/grafana/provisioning/dashboards/dashboards.yml`
- `monitoring/prometheus/prometheus.yml`
- `monitoring/prometheus/alerts.yml`
- `monitoring/loki/loki-config.yaml`

Render services are currently bootstrapped with inline configs in `render.yaml`.

## 7) Validation checklist

1. `metar-to-iwxxm-api/health` returns healthy.
2. `metar-to-iwxxm-api/metrics` returns Prometheus text.
3. `metar-to-iwxxm-auth-v2/metrics` returns Prometheus text.
4. In Grafana, Prometheus datasource is healthy.
5. In Grafana, Loki datasource is healthy.
6. Dashboard panels for request rate/error rate/translation success populate.
