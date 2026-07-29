# 11-verify-impl — S026 / EV-020 (F24 / F25 / F9·F7.g)

> Generated: 2026-07-29  
> Branch: `evolve/EV-020-airmet-quality`  
> Tip: `3027305` (+ T6.4 sign-off commit)  
> Sources: `acceptance-criteria.md`, `e2e-report.md`, `verification-report.md`  
> Decision: **D-S026-E20-11-ac-all** · preview **D-S026-E20-11-preview-no**

## UI preview

| Item | Status |
|------|--------|
| Offered | **Yes** (FE Examples catalog / FileConverter touched) |
| Choice | **No — approve from reports/tests only** (user 2026-07-29) |
| Decision | D-S026-E20-11-preview-no |

## Per-criterion status

### F24 — AIRMET quality

| # | Criterion | T0 evidence | Status |
|---|-----------|-------------|--------|
| F24.1 | AIRMET lint codes registered | TC-F24 A1/A2 packs green | **MET** |
| F24.2 | `airmet-A6-1a-TS` == vendor XML (defaults) | TC-F24-002 | **MET** |
| F24.3 | Golden XSD+SCH | TC-F24-002 pack (+ wmo-quality) | **MET** |
| F24.4 | Negatives → registry diagnostics | TC-F24-004 | **MET** |
| F24.5 | Workbench AIRMET smoke (+ H4–H5) | TC-F24-005 API smoke **PASS**; H4–H5 → **T6.5** | **MET (T0)** / H4–H5 at 13 |

### F25 — WMO METAR/SPECI/TAF + UI gate

| # | Criterion | T0 evidence | Status |
|---|-----------|-------------|--------|
| F25.1 | WMO METAR/SPECI/TAF == vendor (defaults) | TC-F25-001 | **MET** |
| F25.2 | Those goldens validate | TC-F25-001 XSD/SCH + wmo-quality | **MET** |
| F25.3 | Examples = WMO-passers only | Vitest TC-F25-003 / examplesCatalog | **MET** |
| F25.4 | Load WMO example → convert (+ H4–H5) | TC-F25-004 + FileConverter goldens **PASS**; H4–H5 → **T6.5** | **MET (T0)** / H4–H5 at 13 |

### F9 deepen — glossary

| # | Criterion | T0 evidence | Status |
|---|-----------|-------------|--------|
| F9.d1 | Seven-product token meanings | TC-F9-003 | **MET** |
| F9.d2 | YAML/JSON registry loads | TC-F9-004 | **MET** |
| F9.d3 | OpenAIP/F3 miss → designator only | TC-F9-003 | **MET** |

### F7.g deepen

| # | Criterion | T0 evidence | Status |
|---|-----------|-------------|--------|
| F7.g1 | Catalog policy in Vitest | TC-F25-003 / TC-F7-008 | **MET** |

## Journey sign-off (T0)

| Journey | T0 | Browser/T3 | Result |
|---------|----|------------|--------|
| UJ-035 | **PASS** | pending 13 | **Approved** (T0); H4–H5 at T6.5 |
| UJ-036 | **PASS** | pending 13 | **Approved** (T0); H4–H5 at T6.5 |
| UJ-020 deepen | **PASS** | N/A at T0 | **Approved** |
| UJ-032 deepen | **PASS** | pending 13 | **Approved** (T0) |

## User sign-off table

| Fn | Reviewer | Date | Result |
|----|----------|------|--------|
| F24 | user | 2026-07-29 | **APPROVED** (D-S026-E20-11-ac-all) |
| F25 | user | 2026-07-29 | **APPROVED** (D-S026-E20-11-ac-all) |
| F9 deepen | user | 2026-07-29 | **APPROVED** (D-S026-E20-11-ac-all) |
| F7.g deepen | user | 2026-07-29 | **APPROVED** (D-S026-E20-11-ac-all) |

## Next

1. ~~User AC + UI-preview~~ **done** (approve all; no preview)
2. **T6.5** — 13-deploy-smoke (redeploy if API/FE; **H4–H5 required**)
3. Evolve PR to `main` (`do_not_auto_merge: true`)
