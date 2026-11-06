# Decision — Weekly validation catalog GitHub Action

**Session:** EV-weekly-validation-catalog-gha  
**Date:** 2026-10-30  
**Status:** accepted (operator defaults; AskQuestion tooling unavailable; proceed per intake)

## Context

Operators want a weekly view of **what validation issues the staging API is raising now**:
catalog sizes by severity plus live lint/validate counts against a fixed fixture window,
without rewriting the convert UI or lowering coverage floors.

Sibling qa-gap `QG-weekly-api-validation-automation` inventories existing scheduled /
staging workflows; it showed no weekly staging validation-catalog probe yet (only
vendor-sync / mutation / pypi-nightly / load-tests / Staging smoke).

## Decisions

| ID | Choice |
|----|--------|
| D1 | **GHA runners → HTTPS staging API** (not DigitalOcean App Platform job runners). Staging is already the DOKS snapshot Environment used by Deploy / Staging smoke. |
| D2 | Schedule **`0 0 * * 0`** (Sunday 00:00 UTC) + `workflow_dispatch`. |
| D3 | Job uses GitHub Environment **`staging`** (same window as ops/Deploy secrets). |
| D4 | Probe public routes: `GET /health`, `GET /api/v1/lint-issue-catalog`, `GET /api/v1/rule-catalogs`, `POST /api/v1/lint-tac`, `POST /api/v1/validate` with accept fixtures from `packages/tac-validate/tests/fixtures/accept/*_basic.tac`. |
| D5 | **No new product API-key auth** for F21 public routes. Optional Environment secret `STAGING_API_BEARER_TOKEN` (alias `STAGING_API_TOKEN` in script env) may be set for Bearer headers; omit for anonymous public probes. |
| D6 | Report artifact JSON + Markdown; **not** a PR merge gate. Soft-fail sample probes by default; hard-fail on health/catalog failure. |
| D7 | Host-header LB fallback mirrors `scripts/deploy/staging_smoke.sh` (`STAGING_LB_IP` default `143.244.202.13`). |
| D8 | No new ADR — CI ops pattern reuses existing Environment `staging` + public API contract; decisions log is sufficient. |

## CORPUS

- [Corpus: product §F2] [Corpus: product §F15] — deepen quality window only (no new Fn)
- [Corpus: api] — catalog / lint / validate shapes unchanged
- [Corpus: deploy] [Corpus: env-contract] [Corpus: tests] — secrets + TC rows

## Non-goals

- DO App Platform cron jobs
- Committing credentials
- Changing coverage floors or operator UI copy

## Follow-up — live-map probe (2026-10-30)

Operator clarification: the weekly quality window should exercise **live map examples**
(`GET /api/v1/live-map` → convert with correct `product` → validate XML), not fixture soft-fails
that POST the wrong product path.

Thin evolve session: `EV-live-map-convert-validate-probe`  
(`~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-live-map-convert-validate-probe/`).

Proposed D4 amend (not implemented in GHA yet):

- Primary: live-map latest-TAC-per-place convert + XML validate
- Secondary: keep catalog GET severity rollups
- See session `reports/weekly-gha-redesign.md` + `HANDOFF.md`

[Corpus: product §F37] [Corpus: api] [Corpus: deploy]
