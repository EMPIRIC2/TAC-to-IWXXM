# Verification report — 08-verify-build (S067 / EV-057)

> Generated: 2026-08-16  
> Scope: delta refresh after #948 live AC (`D-S067-948-apply=1a`, `D-S067-948-redirect=1a`)  
> Branch: `evolve/EV-057-m0-ready-apex-accumulate-validate`  
> Tip: `0e7833d1`  
> Corpus: [Corpus: tests] [Corpus: product §F7] [Corpus: product §F30] [Corpus: deploy]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | 0 | 0 | `make lint-fast` |
| Format | PASS | 0 | 0 | `make format-check` |
| Typecheck | SKIPPED | delta 08 (`D-S067-08-start=1a`) | — | — |
| Tests (H0c) | PASS | 6 | — | `pytest tests/unit/test_cors_policy.py` |
| Tests (FE EV-057) | PASS | 220 | — | vitest `outputFilename` + `FileConverter` |
| Kustomize overlays | PASS | prod + staging | — | `kubectl kustomize` |
| Live #948 UJ-OPS-002 | PASS | HTTPS/HTTP 301 + TLS SAN | — | curl / openssl |
| Security (pip-audit) | SKIPPED | delta 08 | — | — |
| Performance | SKIPPED | no EV-057 thresholds | — | — |
| Data | SKIPPED | n/a | — | — |

Overall: **PASS**

## Live #948 (prod)

| Request | Result |
|---------|--------|
| `https://tac-to-iwxxm.com/foo?bar=1` | HTTP/2 **301** `Location: https://app.tac-to-iwxxm.com/foo?bar=1` |
| `https://www.tac-to-iwxxm.com/` | HTTP/2 **301** `Location: https://app.tac-to-iwxxm.com/` |
| `http://tac-to-iwxxm.com/foo?bar=1` | HTTP/1.1 **301** → HTTPS app path/query |
| `https://app.tac-to-iwxxm.com/` | HTTP/2 **200** |
| TLS SAN | `tac-to-iwxxm.com`, `www.tac-to-iwxxm.com` |
| `metar-apex-redirect` | 1/1 Ready |

Mechanism: sibling Ingress `metar-frontend-apex` + nginx pod `metar-apex-redirect`
(ingress-nginx v1.12 webhook rejects `$request_uri` on `permanent-redirect`).

## Connectivity artifacts

| Artifact | Present |
|----------|---------|
| `tests/unit/test_cors_policy.py` | yes |
| `tests/smoke/test_staging_connectivity.py` | yes |
| `scripts/deploy/verify_connectivity.sh` | yes |
| CORS on API | `METAR_CORS_ORIGINS` / `config.*.api.corsOrigins` (H0c passed) |

H4–H5 deferred to 12/13. Playwright UJ-057/UJ-058 at 10-e2e.

## Outcome

**PASS** — Phase C gate ready. Next: **09-qa** + **10-e2e** (`D-S067-948-next=1a`).
Promote still held (`D-S067-promote=2b`).
