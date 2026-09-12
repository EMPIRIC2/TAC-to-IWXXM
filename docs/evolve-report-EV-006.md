# Evolve report — S008 general TAC→IWXXM (F6) + validate packages + F8 worker

- **Cycle**: EV-006
- **Session**: S008-general-tac-iwxxm-converter
- **Status**: completed
- **Scope**: F6 tac2iwxxm + F2 package engines + F8 Render worker; F7 Planned only
- **Stages run**: 00, 01, 04, 05, 16, 07, 08, 09, 10, 11
- **Skipped**: 02, 03, 06, 12, 13
- **ADRs**: ADR-013 … ADR-019
- **Deploy**: not this cycle (waived; live H4–H7 deferred)
- **Open issues**: live connectivity; F7; QA-001–003 advisories

## Summary

S008 delivered the general TAC→IWXXM stack (`packages/tac2iwxxm`, `tac-validate`,
`iwxxm-validate`), bulletin conversion API, F6.e UI pickers, gifts cutover with PyO3 gate,
and F8 `apps/worker` ingest with store/quarantine. Implementation verification approved
F6/F2/F8 with documented live waivers. Corpus status for F6 and F8 set to Implemented
(ADR-019).

## Artifacts changed (high level)

- `packages/{tac2iwxxm,tac-validate,iwxxm-validate}/`
- `apps/backend` convert/lint/validate/bulletin routes; gifts removed
- `apps/frontend` product/profile pickers
- `apps/worker` poller + Supabase writers
- `vendor/schemas/iwxxm-us` pin
- Docs: feature-list, spec, journeys, test-plan, api-contract, ADRs 013–019
- Session reports under `docs/sessions/S008-general-tac-iwxxm-converter/reports/`

## Verification

- 08-verify-build: PASS
- 09-qa: pass_with_advisories
- 10-e2e: PASS (Playwright 12/12 after COR hotfix)
- 11-verify-impl: APPROVED (live deferred)
