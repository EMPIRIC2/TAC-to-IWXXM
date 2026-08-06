# E2E Report — S046 / EV-038 (T5.2 / 10-e2e delta)

> Generated: 2026-08-06  
> Scope: **UJ-050** (IWXXM version picker Latest / Previous — #854 / TC-EV038-007)  
> Branch: `evolve/EV-038-iwxxm-corpus-residuals`  
> Corpus: `[Corpus: tests]` · `[Corpus: product]` · `docs/user-journeys.md` §UJ-050

## Journey matrix

| Journey | Mechanism | T0 | T2 connectivity | T3 live |
|---------|-----------|----|-----------------|---------|
| UJ-050 Latest/Previous labels | Vitest SoT + FileConverter; Playwright option text | **PASS** | pending **T5.4** H4–H5 | deferred → 13/15 |
| UJ-005 picker keep-green | existing `f6e-product-profile-pickers` | **PASS** (Vitest) | pending H4–H5 | deferred → 13 |

## T0 results

| Suite | Result |
|-------|--------|
| `iwxxmVersions.test.ts` | PASS — roles → Latest/Previous labels |
| `f6e-product-profile-pickers.workflow.test.tsx` | PASS — option text includes `(Latest)` / `(Previous)` |
| H0c CORS | 6 passed |
| `tests/e2e/` pytest | N/A — browser E2E in `apps/e2e/` |

## T2 / Playwright

| Suite | Result |
|-------|--------|
| `f6e-product-profile-pickers.e2e.spec.ts` **UJ-050** | **added** — asserts `#param-iwxxm-version` option labels contain `(Latest)` / `(Previous)`; run with Compose / live at T5.4 or local `make test-e2e-playwright-smoke` when stack up |
| E2E badge | **70** (was 69) |

## Connectivity notes

- FE #854 shipped (M2); labels sourced from `apps/frontend/src/generated/iwxxm_versions.json`
- **H4–H5 required** at T5.4 / 13-deploy-smoke (S02.M5; FE runtime change)
- Prep: `scripts/deploy/verify_connectivity.sh`; set `LIVE_API_URL` + `LIVE_FRONTEND_URL`
- Non-deployed UI preview offered at M2 (`t2.8-m2-closeout.md`); re-offer at 11-verify-impl if needed

## Overall

**T0: PASS** — production browser proof (H4–H5 / T2–T3) deferred to T5.4.
