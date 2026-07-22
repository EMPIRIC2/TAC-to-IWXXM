# E2E Report — S020 / EV-015 (F20 / UJ-031)

> Generated: 2026-07-22  
> Scope: UJ-031 / TC-F20-001..006  
> Branch: `evolve/EV-015-aerodrome-quality` @ `ca79381`  
> Mode: evolve delta (10-e2e)

## Journey matrix

| Journey / TC | Mechanism | T0 | T2 connectivity | T3 browser |
|--------------|-----------|----|-----------------|------------|
| UJ-031 / TC-F20-001 registry | pytest `tac-validate` | PASS | pending 13 | pending 13 |
| TC-F20-002 TAF goldens | `tac2iwxxm` pytest | PASS | — | — |
| TC-F20-003 SPECI goldens | `tac2iwxxm` pytest (annex3 + iwxxm_us) | PASS | — | — |
| TC-F20-004 negatives / themes | `tac-validate` T1–T3 / S1 / C1 | PASS | — | — |
| TC-F20-005 catalog + lint/convert smoke | backend integration + Vitest FE catalog | PASS | pending 13 (H3 live) | pending 13 (H4–H5) |
| TC-F20-006 SPECI↔METAR misclass | `tac2iwxxm` pytest | PASS | — | — |

## Results

- **Python F20 suite:** 162 passed (registry, themes, goldens, misclass, API smoke)
- **Frontend F20 catalog suite:** 10 passed (3 files — helpers + WorkbenchConsole catalog/taf)
- **Dedicated Playwright F20 spec:** none (F7 remains Planned; smoke under F20 via Vitest + API)

## Connectivity columns

| Column | Status |
|--------|--------|
| T0 in-process | PASS |
| T2 H4–H5 | pending — 13-deploy-smoke (T5.7) |
| T3 live browser UJ | pending — after H4–H5 |

**Overall T0: PASS** — production browser proof deferred to T5.7 with explicit H4–H5 requirement (E15-7 / E15-14).
