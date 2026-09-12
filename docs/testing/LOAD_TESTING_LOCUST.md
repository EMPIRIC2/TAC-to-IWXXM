# Locust Load Testing and Metrics Tracking

This guide adds repeatable load testing for the backend API using Locust, with:

- Profile-based targeting (`local_*`, `staging_*`)
- Auth modes (`bypass`, `bearer`)
- CSV + HTML outputs from Locust
- Prometheus-compatible metrics on a scrape endpoint

## Prerequisites

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install locust prometheus-client
```

## Profile Matrix

Set `LOCUST_PROFILE` to one of:

- `local_bypass` (default)
- `local_auth`
- `staging_bypass`
- `staging_auth`

Each profile can be overridden with env vars:

- `LOCUST_HOST`
- `LOCUST_AUTH_MODE` (`bypass` or `bearer`)
- `LOCUST_AUTH_BASE_URL`
- `LOCUST_IWXXM_VERSION` (default: `2025-2`)
- `LOCUST_VALIDATION_LAYERS` (default: `airport_icao,tac_syntax`)
- `LOCUST_ENABLE_EVALUATION` (`true`/`false`, default `false`)

## Auth Modes

### Bypass Mode

Use when backend runs with auth disabled (`DISABLE_AUTH=true`).

```bash
export LOCUST_PROFILE=local_bypass
```

### Bearer Mode

Requires auth credentials and auth service URL.

```bash
export LOCUST_PROFILE=local_auth
export LOCUST_AUTH_EMAIL="you@example.com"
export LOCUST_AUTH_PASSWORD="your-password"
export LOCUST_AUTH_BASE_URL="http://localhost:8002"
```

## Run Commands

### Interactive UI mode

```bash
cd backend
LOCUST_PROFILE=local_bypass \
locust -f tests/load/locustfile.py
```

- Locust UI: `http://localhost:8089`
- Prometheus metrics: `http://localhost:9646/metrics`

### Headless baseline run

```bash
cd backend
LOCUST_PROFILE=local_bypass \
locust -f tests/load/locustfile.py \
  --headless \
  --users 20 \
  --spawn-rate 2 \
  --run-time 5m \
  --csv test-reports/locust-baseline \
  --html test-reports/locust-baseline.html
```

### Staging authenticated run

```bash
cd backend
LOCUST_PROFILE=staging_auth \
LOCUST_AUTH_EMAIL="you@example.com" \
LOCUST_AUTH_PASSWORD="your-password" \
locust -f tests/load/locustfile.py \
  --headless \
  --users 15 \
  --spawn-rate 1 \
  --run-time 10m \
  --csv test-reports/locust-staging-auth \
  --html test-reports/locust-staging-auth.html
```

## Metrics Tracked

Locust request events are exported as Prometheus metrics with labels:

- `profile`
- `auth_mode`
- `scenario`
- `endpoint`
- `method`
- `status_class`

Series:

- `locust_request_latency_ms` (histogram)
- `locust_requests_total` (counter)
- `locust_request_failures_total` (counter)

Prometheus server controls:

- `LOCUST_PROMETHEUS_ENABLED` (default `true`)
- `LOCUST_PROMETHEUS_PORT` (default `9646`)

## CI Workflow

Automated load runs are defined in [.github/workflows/load-tests.yml](../../.github/workflows/load-tests.yml).

- Scheduled run: daily at `03:00 UTC`
- Authenticated scheduled run: daily at `04:00 UTC` (`staging_auth` profile)
- Manual run: `workflow_dispatch` with profile/user/spawn/runtime inputs
- Artifacts: Locust HTML + CSV files uploaded for 30 days

The authenticated scheduled job auto-skips (without failing the workflow) until all required auth secrets are configured.

Required GitHub secrets for hosted targets:

- `LOAD_TEST_TARGET_URL`
- `LOAD_TEST_AUTH_URL` (required for `*_auth` profiles)
- `LOAD_TEST_EMAIL` (required for `*_auth` profiles)
- `LOAD_TEST_PASSWORD` (required for `*_auth` profiles)

## Scenario Coverage

Current users/scenarios in `backend/tests/load/scenarios.py`:

- Public endpoints (`/health`, versions, schema status, centre info, airport region)
- Conversion endpoint (`/api/v1/convert` with normal and validated payloads)
- Validation endpoints (`/api/v1/validation/validate`, `/validate-multi`)
- Evaluation job workflow (optional, disabled by default)

## Initial KPI Recommendations

Track and compare by profile and auth mode:

- `p95` latency per endpoint family
- Error rate by status class (`4xx`, `5xx`, exceptions)
- Throughput (`requests_total` growth over time)
- Conversion endpoint stability under sustained load
