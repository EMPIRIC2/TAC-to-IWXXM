# Evolve report — F16 SQL ingest live e2e + teardown

- **Cycle**: EV-039
- **Session**: [S047-sql-ingest-live-e2e](sessions/S047-sql-ingest-live-e2e/session-brief.md)
- **Status**: 13 evidence green — pending `D-S047-13` / close
- **Scope**: Deepen F16 — local Compose Postgres/MySQL/SQL Server/SQLite; Playwright live
  upload; teardown for integration + e2e + local. No new Fn. UI preview declined.
  [Corpus: product §F16] [Corpus: tests] [Corpus: journeys §UJ-027]
- **Stages run**: 00, 16, 01, 02, 04, 05, 07, 08, 09, 10, 11, 12, 13 (03/06 skipped — Standard)
- **ADRs**: ADR-029 / ADR-030 (allowlist / egress — no new ADR)
- **Deploy**: PR [#891](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/891) MERGED @ `fea30aba`;
  post-merge CD [31130303373](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31130303373);
  historical CLI tag `20260806224839-7df9f8f`; resume H0c/H1/H4–H5 PASS 2026-08-08
- **Open issues**: none for this cycle (SQL Server live TC skip under QEMU remains harness note;
  operator DB UI restore tracked in [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898) via S050)

## Summary

EV-039 deepened F16 with a live local multi-DB BYOC upload path (Compose mock-byoc + Playwright
`TC-F16-LIVE-*`), async write assert helper, teardown audit across integration/e2e/local, and
docs/make/CI entrypoints. Production does not run SQL containers (F16-R9 OOS). Tip CI on the PR
was blocked by a GitHub Actions outage; CLI deploy + merge proceeded, then post-merge CD succeeded.
Session closeout stalled (unpushed docs branch); resumed 2026-08-08 (`D-S047-resume=2`) to finish 13.

## Artifacts changed

- `apps/e2e` — LIVE SQL Playwright + teardown
- `packages/dissemination` — `live_write_assert` helper
- `docker-compose.yml` / Makefile — mock-byoc profile, `test-e2e-f16-live-sql`, teardown
- `package.json` — `js-yaml` pin ≥4.3.1
- Standing docs: feature-list §F16, test-plan, user-journeys, tech-spec, evolve-decisions
- Session reports under `docs/sessions/S047-sql-ingest-live-e2e/reports/`

## Verification

| Stage | Result |
|-------|--------|
| 08-verify-build | PASS (LIVE TC-F16-LIVE-001/002/004; 003 skip QEMU) |
| 09-qa | PASS with advisories |
| 10-e2e | PASS |
| 11-verify-impl | APPROVED (`D-S047-11=1`; SQL Server waive OK) |
| 12-verify-deploy | APPROVED (`D-S047-12=1`) |
| 13-deploy-smoke | Evidence PASS — see [deploy-smoke.md](sessions/S047-sql-ingest-live-e2e/reports/deploy-smoke.md) |

## Decisions (deploy / close)

| ID | Choice |
|----|--------|
| D-S047-13-cli | CLI deploy after local `make ci` while GHA outage (2026-08-06) |
| D-S047-resume | **2** — resume S047; finish 13 properly then close (2026-08-08) |
| D-S047-13 | pending user approval |
| D-S047-close | pending after 13 |
