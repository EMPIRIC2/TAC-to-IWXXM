# Verification Report

> Generated: 2026-08-06
> Scope: EV-039 / S047 — 08-verify-build after M1+M2; Docker LIVE re-run
> Branch: `evolve/EV-039-sql-ingest-live-e2e` @ `57c645dc` (+ uncommitted harness fixes)
> Corpus: [Corpus: product §F16] [Corpus: tests] TC-F16-LIVE [Corpus: tech-spec] [Corpus: adr/ADR-029]

## Summary

| Check | Status | Findings | Auto-Fixed | Tool |
|-------|--------|----------|------------|------|
| Lint | PASS | 0 | — | ruff + eslint |
| Format | PASS | 0 | — | ruff format + prettier |
| Typecheck | PASS | warnings only (pre-existing tac2iwxxm) | — | basedpyright + tsc |
| Tests (unit) | PASS | full `make test-unit` | — | pytest + vitest |
| H0c CORS | PASS | 6/6 | — | `tests/unit/test_cors_policy.py` |
| Connectivity artifacts | PASS | present | — | `test_staging_connectivity.py`, `verify_connectivity.sh` |
| Security (gitleaks) | PASS | 0 | — | pre-commit gitleaks |
| Security (pip-audit) | PASS | 0 vulns | — | `uv tool run pip-audit` |
| Pattern scan | PASS | 0 | — | rg eval/pickle/keys |
| F16 LIVE (Docker) | PASS* | 001/002/004 green; 003 skipped | harness fixes | Playwright |

\* Overall gate for M1+M2 quality checks: **PASS**. LIVE close with SQL Server waived on this Mac (QEMU) — see failures raised.

## F16 LIVE evidence (Docker API + Compose BYOC)

```
TC-F16-LIVE-001 Postgres  PASS
TC-F16-LIVE-002 MySQL     PASS
TC-F16-LIVE-003 SQL Server SKIPPED (F16_SKIP_SQLSERVER=1)
TC-F16-LIVE-004 SQLite    PASS
```

Stack during run: `metar-iwxxm-backend` / `metar-iwxxm-frontend` / `metar-iwxxm-db` (Docker) + BYOC project `metar-iwxxm-mock-byoc`.

## Failures / issues raised (user)

1. **Colima killed by Playwright webServer** — `start-dev-servers.sh --kill` treated Colima SSH mux as a port owner and SIGKILL’d it (`Cannot connect to Docker daemon`). Mitigated: protect ssh/colima/lima listeners; `PLAYWRIGHT_SKIP_WEBSERVER=1` on LIVE make target.
2. **Compose API missing allowlist** — `docker-compose.yml` did not pass `DISSEMINATION_EGRESS_ALLOWLIST` (empty ⇒ deny). Fixed defaults + BYOC DNS/CIDR for Docker egress.
3. **Stale `.env` Playwright URL** — `PLAYWRIGHT_BASE_URL=http://localhost:5173` caused global-setup timeout. Makefile now defaults to `:18000` / `:18001`.
4. **Docker API ≠ host loopback fixtures** — `127.0.0.1:25432` from inside the API container cannot reach host-published BYOC. Mitigated: `docker network connect` + `F16_DOCKER_API` URI rewrite to `byoc-postgres` / `byoc-mysql`.
5. **Colima `/tmp` bind unreliable** — SQLite LIVE-004 400 until repo `tmp/f16-live` bind mount.
6. **SQL Server** — still skipped on Apple Silicon QEMU (documented waiver path).
7. **Teardown trap cwd** — `compose-mock-byoc-down` failed after `cd apps/e2e`; trap now uses `make -C "$(CURDIR)"`.

## Uncommitted harness fixes (not committed — awaiting user)

- `start-dev-servers.sh` — refuse to kill Colima/Docker listeners
- `apps/e2e/playwright.config.ts` — `PLAYWRIGHT_SKIP_WEBSERVER`
- `Makefile` — LIVE Docker defaults + trap fix + URL overrides
- `docker-compose.yml` — allowlist / CORS / `tmp/f16-live` volume
- `apps/e2e/uj027-f16-live-sql.e2e.spec.ts` — `F16_DOCKER_API` URI rewrite + SQLite shared path
- `.gitignore` — `tmp/` (if appended)

## Next (paused per user)

- Commit harness fixes (user ask)
- Continue Standard route: **09-qa** → 10-e2e → …
- Optional: document Docker LIVE recipe in tech-spec delta
