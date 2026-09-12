# E2E Report — S025 / EV-019 (F23 / UJ-034)

> Generated: 2026-07-29  
> Scope: UJ-034 / TC-F23-001..006  
> Branch: `evolve/EV-019-sigmet-quality` @ `846d50f` (+ T5.5 report)  
> Mode: evolve delta (10-e2e) · Lean+build

## Journey matrix

| Journey / TC | Mechanism | T0 | T2 connectivity | T3 browser |
|--------------|-----------|----|-----------------|------------|
| UJ-034 / TC-F23-001 registry | pytest `tac-validate` | **PASS** | — | — |
| TC-F23-002 general SIGMET goldens | `tac2iwxxm` pytest | **PASS** | — | — |
| TC-F23-003 VA SIGMET goldens | `tac2iwxxm` pytest | **PASS** | — | — |
| TC-F23-004 negatives / themes G1–G2 / V1 / C1 | `tac-validate` F23 packs | **PASS** | — | — |
| TC-F23-005 catalog + lint/convert smoke | backend integration + Vitest FE catalog | **PASS** | **PASS** (13 live) | **PASS** (H4–H5) |
| TC-F23-006 VA↔general↔VAA adjacency | `tac2iwxxm` pytest | **PASS** | — | — |

## Results

| Suite | Tests | Status |
|-------|-------|--------|
| Dedicated TC-F23-001..006 modules | **92** passed | **PASS** |
| `make test-sigmet-quality` | **134** tac-validate + **39** tac2iwxxm | **PASS** |
| Frontend catalog SIGMET/VA Vitest | **4** (`WorkbenchConsole.catalog-sigmet.test.tsx`) | **PASS** |
| Dedicated Playwright F23 spec | none (F7 remains Planned; smoke under F23 via Vitest + API) | — |

### Commands

```bash
make test-sigmet-quality
uv run pytest \
  packages/tac-validate/tests/test_tc_f23_*.py \
  packages/tac2iwxxm/tests/test_tc_f23_*.py \
  apps/backend/tests/integration/test_tc_f23_005_sigmet_catalog_smoke.py \
  --no-cov -q
# 92 passed
cd apps/frontend && pnpm exec vitest run \
  src/app/components/WorkbenchConsole.catalog-sigmet.test.tsx
# 4 passed
```

## Connectivity columns

| Column | Status |
|--------|--------|
| T0 in-process | **PASS** |
| T2 H4–H5 | **PASS** — 13-deploy-smoke (2026-07-29); H4–H5 + live SIGMET catalog/lint/convert |
| T3 live browser UJ | deferred — F7 Planned; product-path smoke via API + FE catalog live |

**Overall T0: PASS** · **Overall T2 (13): PASS** (H4–H5 + live F23 catalog/lint/convert).
