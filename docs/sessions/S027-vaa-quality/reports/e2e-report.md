# E2E Report — S027 / EV-021 (F26 / F27 / UJ-037 / UJ-038)

> Generated: 2026-07-30  
> Scope: UJ-037 / UJ-038 (+ UJ-032 deepen)  
> Branch: `evolve/EV-021-vaa-quality` @ `0886093`  
> Mode: evolve delta (10-e2e) · Lean+build+11

## Journey matrix

| Journey / TC | Mechanism | T0 | T2 connectivity | T3 browser |
|--------------|-----------|----|-----------------|------------|
| UJ-037 / TC-F26-001 V1 registry | `tac-validate` pytest | **PASS** | — | deferred → 13 |
| TC-F26-002/003 annex3 goldens | `tac2iwxxm` pytest | **PASS** | — | — |
| TC-F26-004 C1 / negatives | `tac2iwxxm` pytest | **PASS** | — | — |
| TC-F26-005 API smoke | backend integration | **PASS** | **13** | **13** |
| TC-F26-006 adjacency | `tac2iwxxm` pytest | **PASS** | — | — |
| UJ-038 / TC-F27-001 T1 registry | `tac-validate` pytest | **PASS** | — | deferred → 13 |
| TC-F27-002/003 annex3 goldens | `tac2iwxxm` pytest | **PASS** | — | — |
| TC-F27-004 C1 / negatives | `tac2iwxxm` pytest | **PASS** | — | — |
| TC-F27-005 API smoke | backend integration | **PASS** | **13** | **13** |
| TC-F27-006 adjacency | `tac2iwxxm` pytest | **PASS** | — | — |
| UJ-032 deepen / TC-F7-008 Golden examples | Vitest FileConverter | **PASS** | — | deferred → 13 |
| Examples catalog VAA/TCA unlock (S02.M2) | Vitest `examplesCatalog` | **PASS** | **13** H4–H5 | deferred → 13 |
| `splitManualEntries` VAA/TCA | Vitest `tacProduct` | **PASS** | — | — |

## Results

| Suite | Tests | Status |
|-------|-------|--------|
| Dedicated F26/F27 + API smoke + coverage helpers | **89** passed | **PASS** |
| Frontend catalog + tacProduct Vitest | **26** passed | **PASS** |
| FileConverter Golden examples (TC-F7-008 C2–C4) | **6** passed | **PASS** |
| Dedicated Playwright F26/F27 spec | none (F7 Planned; smoke via Vitest + API) | — |

### Commands

```bash
uv run pytest \
  packages/tac-validate/tests/test_tc_f26_*.py \
  packages/tac-validate/tests/test_tc_f27_*.py \
  packages/tac2iwxxm/tests/test_tc_f26_*.py \
  packages/tac2iwxxm/tests/test_tc_f27_*.py \
  packages/tac2iwxxm/tests/test_vaa_tca_coverage_helpers.py \
  apps/backend/tests/integration/test_tc_f26_005_f27_005_vaa_tca_smoke.py \
  --no-cov -q
# 89 passed

cd apps/frontend && pnpm exec vitest run \
  src/fixtures/examples/examplesCatalog.test.ts \
  src/utils/tacProduct.test.ts
# 26 passed

cd apps/frontend && pnpm exec vitest run \
  src/app/components/FileConverter.test.tsx -t "Golden examples"
# 6 passed
```

## Connectivity columns

| Column | Status |
|--------|--------|
| T0 in-process | **PASS** |
| T2 H4–H5 | pending — T6.5 / 13-deploy-smoke (H4–H5 required; FE catalog + API touched) |
| T3 browser | deferred → 13 / live |

## Verdict

**PASS** — handoff T6.4 / 11-verify-impl (per-Fn AC F26/F27).
