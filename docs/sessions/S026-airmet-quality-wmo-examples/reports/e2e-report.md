# E2E Report — S026 / EV-020 (F24 / F25 / UJ-035 / UJ-036)

> Generated: 2026-07-29  
> Scope: UJ-035 / UJ-036 (+ UJ-020 / UJ-032 deepen)  
> Branch: `evolve/EV-020-airmet-quality` @ `c963a0a`  
> Mode: evolve delta (10-e2e) · Lean+build+11

## Journey matrix

| Journey / TC | Mechanism | T0 | T2 connectivity | T3 browser |
|--------------|-----------|----|-----------------|------------|
| UJ-035 / TC-F24-001 A1 header | pytest `tac-validate` | **PASS** | — | deferred → 13 |
| TC-F24 A2 phenomenon | `tac-validate` | **PASS** | — | — |
| TC-F24-002 AIRMET annex3 goldens | `tac2iwxxm` pytest | **PASS** | — | — |
| TC-F24-004 A4 negatives | `tac2iwxxm` pytest | **PASS** | — | — |
| TC-F24-005 / TC-F25-004 API smoke | backend integration | **PASS** | **13** | **13** |
| UJ-036 / TC-F25-001 METAR/SPECI/TAF goldens | `tac2iwxxm` pytest | **PASS** | — | — |
| TC-F25-003 Examples catalog WMO-passers | Vitest FE | **PASS** | **13** H4–H5 | deferred → 13 |
| UJ-020 deepen / TC-F9-003/004 glossary | `tac2iwxxm` pytest | **PASS** | — | — |
| UJ-032 deepen / TC-F7-008 Golden examples | Vitest FileConverter | **PASS** | — | deferred → 13 |

## Results

| Suite | Tests | Status |
|-------|-------|--------|
| Dedicated TC-F24 / F25 / F9 modules + API smoke | **57** passed | **PASS** |
| `make test-wmo-quality` | **215** passed, 9 skipped | **PASS** |
| Frontend catalog Vitest (examples + WorkbenchConsole) | **22** passed | **PASS** |
| FileConverter Golden examples (TC-F7-008 C2–C4) | **6** passed | **PASS** |
| Dedicated Playwright F24/F25 spec | none (F7 Planned; smoke via Vitest + API) | — |

### Commands

```bash
make test-wmo-quality
uv run pytest \
  packages/tac-validate/tests/test_tc_f24_*.py \
  packages/tac2iwxxm/tests/test_tc_f24_*.py \
  packages/tac2iwxxm/tests/test_tc_f25_*.py \
  packages/tac2iwxxm/tests/test_tc_f9_003_004_decode_glossary.py \
  apps/backend/tests/integration/test_tc_f24_005_f25_004_wmo_smoke.py \
  --no-cov -q
# 57 passed
cd apps/frontend && pnpm exec vitest run \
  src/fixtures/examples/examplesCatalog.test.ts \
  src/app/components/WorkbenchConsole.catalog.test.tsx \
  src/app/components/WorkbenchConsole.catalog-taf.test.tsx \
  src/app/components/WorkbenchConsole.catalog-sigmet.test.tsx
# 22 passed
cd apps/frontend && pnpm exec vitest run \
  src/app/components/FileConverter.test.tsx -t "Golden examples"
# 6 passed
```

## Connectivity columns

| Column | Status |
|--------|--------|
| T0 in-process | **PASS** |
| T2 H4–H5 | pending — T6.5 / 13-deploy-smoke (H4–H5 required; FE catalog + API touched) |
| T3 live browser UJ | deferred to 13 — product-path smoke via API + FE catalog Vitest at T0 |

**Overall T0: PASS** · **Overall T2 (13): pending**.
