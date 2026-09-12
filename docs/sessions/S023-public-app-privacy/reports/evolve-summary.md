# Evolve summary — EV-017 / S023 (public app privacy)

> Completed: 2026-07-28  
> Issue: [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)  
> Branch: `evolve/EV-017-public-app-privacy`  
> Features: **F21**, **F22**; deepen F5/F7.h; Auth teardown (ADR-031)

## Outcome

Public unauthenticated operator app + privacy preference center shipped and live-smoke verified.
Operator Auth / JWT path removed; work history is IndexedDB-only; GPC honored.

## Stages

| Stage | Result |
|-------|--------|
| 00 / 16 / 01 / 02 | Scope lock F21/F22; Phase A pass |
| 04 | ADR-031 + execution plan |
| 07–08 | M1–M7 build; verify-build PASS |
| 09–10 | QA pass_with_advisories; T0 E2E PASS |
| 11 | F21/F22 approved; UI preview declined; T3→13 |
| 12 | Deploy checklist READY |
| 13 | Validate-existing; H0c–H5 PASS; Playwright 5/5; API `SUPABASE_*` cleanup |

## Live

- API: https://metar-to-iwxxm-api.onrender.com  
- FE: https://metar-to-iwxxm-frontend-v4-web.onrender.com  
- Post-cleanup API deploy: `dep-d9kii12jobas73fl4bi0`

## Artifacts

- `reports/verify-impl.md`, `deploy-checklist.md`, `deploy-smoke.md`
- `docs/reports/implementation-verification.md`
- `docs/CHANGELOG.md` (S023 finalized)

## Follow-ups (optional)

- Push/merge remaining evolve-branch docs + E2E locator fix to `main`
- 15-service-health / 17-retrospective if desired
- Close #783 when PR train lands
