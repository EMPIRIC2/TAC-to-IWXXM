# DOKS `metar-worker` poller hardening (EV-033 / F8)

## Why

Cutover left `INGEST_POLLER_URL=REPLACE_ME_INGEST_POLLER_URL`, which is not a valid
HTTPS feed. Keep **replicas at 0** until the secret is a probed `https://` URL.

## Non-prod fixture (default when no operational feed)

```
https://raw.githubusercontent.com/EMPIRIC2/TAC-to-IWXXM/main/apps/worker/tests/fixtures/ingest_feed.json
```

## Do not copy stale Render URLs

After DOKS cutover, Render worker/API services may be **suspended** and old
`INGEST_POLLER_URL` values (fork/branch raw.githubusercontent.com links) often
**404**. Always:

1. `python3 scripts/deploy/validate_ingest_poller_url.py --probe "$URL"`
2. Patch the DOKS secret
3. `bash scripts/deploy/doks_worker_poller_preflight.sh --probe --scale-up`

## Fail-closed ops

| Step | Command |
|------|---------|
| Validate + scale 0 if bad | `bash scripts/deploy/doks_worker_poller_preflight.sh --fail-closed` |
| Probe + scale to 1 | `bash scripts/deploy/doks_worker_poller_preflight.sh --probe --scale-up` |
| CrashLoop check | `bash scripts/deploy/check_worker_crashloop.sh` |

## Alerts

- **Now (no Prometheus operator):** run `check_worker_crashloop.sh` in smoke/cron.
- **When kube-prometheus-stack exists:**  
  `kubectl apply -f deploy/doks/observability/prometheusrule-metar-worker.yaml`

## Manifest defaults

- `deploy/doks/base/deployment-worker.yaml` — `replicas: 0`
- `deploy/doks/base/secret-worker.yaml` — stub only; never apply blindly over live secrets
