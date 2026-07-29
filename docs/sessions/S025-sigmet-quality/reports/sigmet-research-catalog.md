# SIGMET + VA SIGMET research catalog — S025 / EV-019

> **T0.1** (E19-16=B · E19-20=B+A). Full mining dig for **General SIGMET + VA SIGMET**.
> Cite external / paywalled sources; do **not** copy Annex 3 / Manual-on-Codes prose into
> wheels. Map F23 themes → registry codes + fixtures in M1–M4.
> **Sibling products** (#738 TC SIGMET, #731 AIRMET, #736 VAA, #737 TCA, #740/#741) get
> **light cite-only notes** only — not fixture work this cycle.

**Tickets:** [#733](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/733) General SIGMET ·
[#739](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/739) VA SIGMET  
**HARD themes:** F23 G1–G3 / V1–V3 / C1 (S1.M1; kill-switch AskQuestion — no silent defer)  
**Naming:** Always “F23 theme Gn” vs pipeline “gate Gn” (S6.M1 / D-S025-EV019-s6m1-1)  
**Predecessor peers:** [taf-speci-research-catalog.md](../../S020-aerodrome-quality/reports/taf-speci-research-catalog.md)
(F20); [metar-research-catalog.md](../../S015-metar-lint-quality/reports/metar-research-catalog.md) (F15)

---

## Sources

| Source | Access | Role for F23 |
|--------|--------|--------------|
| Vendor `TAC-to-XML-Guidance.txt` (2025-2) | In-repo `vendor/schemas/iwxxm/2025-2/IWXXM/examples/` · upstream [wmo-im/iwxxm v2025-2](https://github.com/wmo-im/iwxxm/blob/v2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt) | **Primary encode cookbook** — AIRMET/SIGMET section + All-reports common + AirspaceVolume |
| FM 205 / WMO-No. 306 Vol I.3 Part D | Cite [WMO-306-vI-3-2023-mining-notes.md](../../../domain/mining/WMO-306-vI-3-2023-mining-notes.md); runtime pin → vendor 2025-2 XSD+SCH | Authoritative IWXXM representation |
| ICAO Annex 3 (Ch.7 + App 6) | **Paywall** — cite [icao-annex-3-mining-notes.md](../../../domain/mining/icao-annex-3-mining-notes.md) only | SARPs: one-phenomenon; validity; WS/WV/WC split |
| EUR Doc 014 (5th Ed. 2023) | **Public** — [icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md](../../../domain/mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) | TAC shape; AHL `WS`/`WV`/`WC`→`LS`/`LV`/`LY`; CNL; App C examples (informative) |
| codes.wmo.int | Public — [RULE_SOURCE_URLS.md](../../../domain/rules/RULE_SOURCE_URLS.md) | SigWxPhenomena; nilReason; MetFeature |
| Official IWXXM examples | Vendor `sigmet-A6-1a-TS`, CNL `…-1b-CNL`, `sigmet-VA-EGGX`, TC `sigmet-A6-2-TC` | Golden seeds (TC example cite-only this cycle) |
| ISSUE_CATALOG / ADR-028 | In-repo | Extend SCREAMING_SNAKE codes; optional `product`/`tags` (`sigmet`, `va_sigmet`) |
| Issue exceptional-rule tables | #733 / #739 bodies | Acceptance checklist for encode + fixtures |

**2025-2 corrections:** do **not** encode removed METAR `runwayState` / `CLRD` / `R88` /
`R99` / `SNOCLO` deposit mappings from older guidance rows (not SIGMET fields, but keep
encode cookbook hygiene shared with F15/F20).

**API wire:** HTTP `product=sigmet` only; package selects `iwxxm:SIGMET` vs
`iwxxm:VolcanicAshSIGMET` from TAC (VA phenomenon / `WV` AHL) — E19-13=A.

---

## Themes → work items

| ID | Theme | Lint (F12/F23) | Convert (F6.d) | Validate / goldens |
|----|-------|----------------|----------------|--------------------|
| **G1** | General exceptional (CNL, point→circle, single alt, STNR, polygon/line CRS) | Registry + accept/negatives | Guidance AIRMET/SIGMET + AirspaceVolume tables | SCH |
| **G2** | Sequence / validity / FIR·CTA / phenomenon / movement·intensity | Checklist rules; one-phenomenon; validity caps | Observed/forecast + optional forecast positions | SCH |
| **G3** | General SIGMET golden convert + SCH | — | Expand annex3 (`sigmet-A6-1a-TS`, CNL, …); root `iwxxm:SIGMET` | M-xsd / M-sch / M-golden |
| **V1** | VA-specific (volcano, ash geometry/forecast, `NO VA EXP`, CNL FIR-moved) | Registry + negatives | `VolcanicAshSIGMET` fields | SCH |
| **V2** | VA ↔ general SIGMET ↔ VAA adjacency | Product/root guards | Content-selected root under `product=sigmet`; never VAA | TC-F23-006 |
| **V3** | VA SIGMET golden convert + SCH | — | Expand annex3 (`sigmet-VA-EGGX`, …); root `iwxxm:VolcanicAshSIGMET` | M-xsd / M-sch / M-golden |
| **C1** | Common rules (all reports) | Where TAC tokens apply | `reportStatus` / `permissibleUsage`; `translationFailedTAC`; 2-D CRS; nilReasons; one report/TAC | Round-trip |

---

## Theme detail — General SIGMET (F23 themes G1–G3)

### G1 — Exceptional rules (#733 + Guidance AIRMET/SIGMET + AirspaceVolume)

| TAC condition | Encode (Guidance + #733) | Lint intent |
|---------------|--------------------------|-------------|
| `CNL` | `isCancelReport=true`; `cancelledReportSequenceNumber` + `cancelledReportValidPeriod`; **absent** `phenomenon` / `analysis` | CNL shape; no phenomenon body |
| Single coordinate point | `gml:CircleByCenterPoint` with `gml:radius` **0** | Point geometry accepted; not silent polygon |
| Single altitude | Same value in `aixm:lowerLimit` and `aixm:upperLimit` | Single-level token |
| `STNR` | Empty `directionOfMotion` + nilReason `…/inapplicable`; `speedOfMotion` **0** | Stationary movement |
| Polygon or line | GML with declared CRS (`srsName`, `srsDimension="2"`, `axisLabels`) | CRS present; coordinate order |
| `TOP ABV` / `TOP BLW` | AirspaceVolume guidance (upper/max limits + nilReasons) | Level grammar |

**EUR Doc 014 cites (public):** CNL remaining-period shape; **no `COR`** for SIGMET
(cancel + re-issue) — PDF mining notes §Key findings. Prefer Annex 3 / Guidance for
global encode; EUR for TAC lint messaging.

**Baseline fixtures today:** `packages/tac-validate/tests/fixtures/negative/sigmet/` —
`multi_phenomenon.tac`, `missing_valid.tac` only.  
**Gap:** accept pack + G1 negatives (CNL bad shape, STNR, point, CRS) with registry codes
tagged `sigmet`.

### G2 — Sequence / validity / FIR·CTA / phenomenon / movement·intensity

| Concern | Encode / SARPs cite | Lint intent |
|---------|---------------------|-------------|
| First line | `CCCC SIGMET [seq] VALID YYGGgg/YYGGgg CCCC-` (EUR Doc 014) | Sequence + VALID present |
| Validity | WS ≤ 4 h (Annex 3 / EUR); midnight YY rollover | Duration / midnight guards |
| One phenomenon | General SIGMET = non-VA/non-TC; one SigWx phenomenon | Reject multi-phenomenon (existing negative) |
| FIR / CTA | Affected airspace identity | Location / FIR tokens |
| OBS / FCST | Analysis time + observed or forecast conditions; optional forecast positions | Movement / intensity groups |
| AHL | TAC `WS` → IWXXM `LS` | Bulletin heading when packed |

**Gap:** checklist rules beyond multi_phenomenon / missing_valid; movement INTSF/WKN/NC;
FIR designator shape.

### G3 — Goldens

- Expand annex3 general SIGMET goldens beyond current product_matrix coverage.
- Seeds: `sigmet-A6-1a-TS`, CNL `…-1b-CNL`.
- Assert root `iwxxm:SIGMET` for pinned `iwxxm_version` (esp. 2025-2).
- Round-trip convert → `iwxxm-validate` (M-xsd / M-sch).
- EUR App C TAC examples = **informative** only; prefer official WMO example pairs for CI.

---

## Theme detail — VA SIGMET (F23 themes V1–V3)

### V1 — VA-specific (#739 + Guidance)

| TAC condition | Encode | Lint intent |
|---------------|--------|-------------|
| Apply general SIGMET mapping first | Same G1/G2 geometry / CNL / STNR / levels | Shared family rules |
| Volcano identity | Erupting volcano / name / position (METCE) as schema requires | Volcano group present when VA |
| Ash geometry / forecast position | Observed/estimated + forecast collections | Ash location groups |
| `NO VA EXP` | Empty member under `VolcanicAshSIGMETPositionCollection` + nilReason `…/nothingOfOperationalSignificance` | VA absence token |
| CNL FIR-moved-ash | Cancel may identify FIR to which ash has moved (Annex 3 / #739) | CNL + MOV TO FIR shape |
| AHL | TAC `WV` → IWXXM `LV` | Heading / product hint |

**Do not** use VAA Advisory guidance rows (`UNKNOWN` volcano name, `NOT PROVIDED` status
enums under Advisory types) as VA **SIGMET** encode — those are #736 / VAA path.

### V2 — Adjacency (TC-F23-006)

| Input | Must produce | Must not |
|-------|--------------|----------|
| General non-VA/TC SIGMET TAC + `product=sigmet` | `iwxxm:SIGMET` | `VolcanicAshSIGMET` / VAA |
| VA SIGMET TAC (VA / `WV`) + `product=sigmet` | `iwxxm:VolcanicAshSIGMET` | Plain `SIGMET` silent; VAA root |
| VAA advisory TAC | `product=vaa` / `VolcanicAshAdvisory` | Treated as VA SIGMET |
| TC SIGMET TAC | OOS this cycle (#738) — cite; do not silent-succeed as general if detectable | — |

### V3 — Goldens

- Expand annex3 VA SIGMET goldens; seed `sigmet-VA-EGGX`.
- Assert root `iwxxm:VolcanicAshSIGMET`.
- Round-trip M-xsd / M-sch.
- Still submitted with HTTP `product=sigmet` (E19-13).

---

## Theme detail — Common (F23 theme C1)

Reuse F20 C1 pattern:

| Rule | Lint surface? | Convert |
|------|---------------|---------|
| `reportStatus` / `permissibleUsage` | Limited (SIGMET rarely AMD/COR — EUR: no COR) | Required on report |
| `translationFailedTAC` | No TAC token | Convert-only; defer with rationale if no surface |
| 2-D CRS attrs | Partial (polygon/line cases overlap G1) | Always on geometry |
| nilReasons | Token-driven (STNR, NO VA EXP, …) | Correct WMO URIs |
| One IWXXM per TAC report | Bulletin multi-report awareness | Packing / COLLECT OOS |

---

## Sibling notes (E19-20 light / cite-only)

| Issue | Product | Note this cycle |
|-------|---------|-----------------|
| [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738) | TC SIGMET `TropicalCycloneSIGMET` | Same family exceptional table + METCE TropicalCyclone; AHL `WC`→`LY`; example `sigmet-A6-2-TC`. **OOS** fixtures. |
| [#731](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/731) | AIRMET | Shares Guidance AIRMET/SIGMET section + EUR Part 4; AHL `WA`→`LW`. **OOS**. |
| [#736](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/736) | VAA | Distinct Advisory root; adjacency only under V2. **OOS** encode. |
| [#737](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/737) | TCA | Cite-only. |
| #740 / #741 | SWX / VONA | Cite-only; VONA absent from Guidance. |

Shared C1 common rules may touch these products only when a code is truly product-agnostic —
do not expand sibling fixture packs under F23.

---

## Code anchors (implementation)

| Area | Path |
|------|------|
| Convert | `packages/tac2iwxxm/src/tac2iwxxm/products/sigmet_airmet.py` |
| Product matrix | `packages/tac2iwxxm/tests/test_tc_f6_001_002_product_matrix.py` |
| US profile | `packages/tac2iwxxm/tests/test_tc_f6_003_taf_sigmet_airmet_iwxxm_us.py` |
| Lint products | `packages/tac-validate/src/tac_validate/products.py` |
| Existing negatives | `packages/tac-validate/tests/fixtures/negative/sigmet/` |
| FE catalog | Extend filters/copy for `sigmet` / VA tags (E19-17; T5.1–T5.2) |
| CI | Dedicated `.github/workflows/sigmet-quality.yml` (E19-19; T0.3) |

---

## Acceptance crosswalk

| F23 AC / TC | Themes | Milestones |
|-------------|--------|------------|
| TC-F23-001 registry completeness | All | M4 T4.6 |
| TC-F23-002 general goldens | G1–G3 | M1–M2 |
| TC-F23-003 VA goldens | V1–V3 | M3–M4 |
| TC-F23-004 negatives | G1–G2 / V1 | M1 / M3 |
| TC-F23-005 workbench + catalog | Smoke + FE | M5 |
| TC-F23-006 adjacency | V2 | M3 |
| Matrix G1–G3 / V1–V3 / C1 closed or deferred | All | M2 T2.3 / M4 T4.5 |

---

## Theme close log

| Theme | Decision | Date | Notes |
|-------|----------|------|-------|
| G1–G3 | **Closed** (`D-S025-T2.3-A`) | 2026-07-29 | Lint M1 + convert T2.2 + TC-F23-002 goldens; residuals in COVERAGE_MATRIX |
| V1–V3 / C1 | Open | — | M3–M4 |
