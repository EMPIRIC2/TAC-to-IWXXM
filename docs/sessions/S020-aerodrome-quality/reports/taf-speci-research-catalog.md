# TAF + SPECI research catalog — S020 / EV-015

> **T0.1** (E15-13=C). Full mining dig for **TAF + SPECI only**. Cite external /
> paywalled sources; do **not** copy Annex 3 / FMH / Manual-on-Codes prose into
> wheels. Map themes → registry codes + fixtures in M1–M4. Sibling products
> (#731/#733/#736–#741) are **cite-only** stubs here.

**Tickets:** [#735](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/735) TAF ·
[#734](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/734) SPECI  
**HARD themes:** T1–T4 / S1–S3 / C1 (S1.M1; kill-switch AskQuestion — no silent defer)  
**Predecessor:** [metar-research-catalog.md](../../S015-metar-lint-quality/reports/metar-research-catalog.md)
(R1–R8 closed; SPECI shared pack exists — deepen under S1–S3)

---

## Sources

| Source | Access | Role for F20 |
|--------|--------|--------------|
| Vendor `TAC-to-XML-Guidance.txt` (2025-2) | In-repo `vendor/schemas/iwxxm/2025-2/IWXXM/examples/` · upstream [wmo-im/iwxxm v2025-2](https://github.com/wmo-im/iwxxm/blob/v2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt) | **Primary encode cookbook** — TAF section + METAR/SPECI section + All-reports common rules |
| FM 205 / WMO-No. 306 Vol I.3 Part D | Cite [WMO-306-vI-3-2023-mining-notes.md](../../../domain/mining/WMO-306-vI-3-2023-mining-notes.md); runtime pin → vendor FM205.adoc / 2025-2 XSD+SCH | Authoritative IWXXM representation; NIL–CNL req classes |
| ICAO Annex 3 (20th + Amd 81) | **Paywall** — cite [icao-annex-3-mining-notes.md](../../../domain/mining/icao-annex-3-mining-notes.md) only | SARPs: SPECI App 3 §2.3; TAF App 5 / Tables A5-1·A5-2; Ch.6 validity |
| US FMH-1 (2019) | Cite [fmh1-2019-mining-notes.md](../../../domain/mining/fmh1-2019-mining-notes.md) | `iwxxm_us` SPECI body + §2.5.2 criteria (**not** TAF SoT) |
| codes.wmo.int | Public — [RULE_SOURCE_URLS.md](../../../domain/rules/RULE_SOURCE_URLS.md) | Weather / nilReason / AviationColourCode URIs |
| Official IWXXM examples | Vendor `…/examples/taf-A5-*.xml` · `speci-*.xml` (as pinned) | Golden seeds |
| ISSUE_CATALOG / ADR-028 | In-repo | Extend SCREAMING_SNAKE codes; optional `product`/`tags` (`taf`, `speci`) |
| Issue exceptional-rule tables | #735 / #734 bodies | Acceptance checklist for encode + fixtures |

**2025-2 corrections (both products):** do **not** encode removed `runwayState` /
`CLRD` / `R88` / `R99` / `SNOCLO` deposit mappings from older guidance rows.

**OOS siblings (cite-only):** AIRMET #731 · SIGMET family #733/#738/#739 · VAA #736 ·
TCA #737 · SWX #740 · VONA #741 — share C1 common rules only when needed.

---

## Themes → work items

| ID | Theme | Lint (F12/F20) | Convert (F6) | Validate / goldens |
|----|-------|----------------|--------------|--------------------|
| **T1** | TAF NIL / CNL / AMD / COR | Registry + accept/negatives; NIL/CNL end-message shape (A5-1 paraphrase) | `reportStatus` AMD/COR; NIL → empty `baseForecast` + `…/nil/missing`; CNL → `isCancelReport` + `cancelledReportValidPeriod`; omit valid/base/change | SCH on cancel/nil shapes |
| **T2** | Change groups FM / BECMG / TEMPO / PROB + TL / AT | PROB only 30\|40; PROB must not qualify BECMG/FM; ordered groups; TL/AT grammar | Issue/aerodrome/validity → report; initial → `baseForecast`; FM/BECMG/TEMPO/PROB → ordered `changeForecast`; FM begin→end; TL start→TL; AT → time instant | SCH order / period |
| **T3** | TX/TN; CAVOK / NSC / NSW / VV/// | TX/TN pairs on **base only**; CAVOK checklist; NSC/NSW tokens; VV/// omit-without-nil | TX/TN on baseForecast only; CAVOK → `cloudAndVisibilityOK`; NSC/NSW → `nothingOfOperationalSignificance`; VV/// → omit verticalVisibility **no** nilReason | XSD/SCH |
| **T4** | TAF golden convert + SCH | — | Expand annex3 (+ iwxxm_us) TAF goldens; root `iwxxm:TAF` | M-xsd / M-sch / M-golden |
| **S1** | SPECI exceptional rules (shared METAR/SPECI) | Deepen pack beyond F15 R1–R8: NIL obs; CAVOK; NSC/NCD; NOSIG; NSW-in-trend; `//` / VV///; RVR missing vs notObservable; `dddVddd` CCW→CW | Same field map as METAR; root `iwxxm:SPECI`; 2025-2 no runwayState | Existing + expand goldens |
| **S2** | SPECI↔METAR mis-classification | Product hint / Auto-detect; never silent cross-product pass | Per-report identity | TC-F20-006 |
| **S3** | SPECI golden convert + SCH | — | Expand annex3 / iwxxm_us SPECI goldens; root `iwxxm:SPECI` | M-xsd / M-sch |
| **C1** | Common rules (all reports) | Where lint applies: AMD/COR status tokens; one-report bulletin awareness | `reportStatus` + `permissibleUsage`; translation-failed TAC; 2-D CRS; code-list URIs; `xsi:nil` + nilReason; one IWXXM report per TAC report | Round-trip |

---

## Theme detail — TAF (T1–T4)

### T1 — NIL / CNL / AMD / COR

| TAC | Encode (Guidance + #735) | Lint intent |
|-----|--------------------------|-------------|
| `NIL` | Empty `iwxxm:baseForecast` + `nilReason=…/missing` | NIL ends message; no body groups (`INVALID_NIL`-class) |
| `CNL` | `isCancelReport=true`; `cancelledReportValidPeriod` set; **absent** `validPeriod` / `baseForecast` / `changeForecast` | CNL shape; no forecast body |
| `AMD` / `TAF AMD` | `reportStatus="AMENDMENT"` | Modifier present INFO/ERROR as registry |
| `COR` / `TAF COR` | `reportStatus="CORRECTION"` | Same |

**Annex 3 cites (paywall):** Table **A5-1** template identifiers; Ch.6 §6.1–6.2 cancel /
single-valid-TAF policy — see mining notes §7. Do not ship numeric thresholds in-repo.

**Baseline fixtures today:** negatives `missing_cccc`, `missing_issue_time`,
`missing_validity`, `bad_cnl_shape` under `packages/tac-validate/tests/fixtures/negative/taf/`.
**Gap:** accept fixtures + registry codes tagged `taf` for each T1 case.

### T2 — FM / BECMG / TEMPO / PROB + TL / AT

| TAC indicator | Encode (#735 principal + Guidance where present) | Lint / Annex cite |
|---------------|--------------------------------------------------|-------------------|
| `FM` | `changeForecast` period begins at FM time → applicable endpoint; **supersedes** prior elements | Table A5-2; App 5 §1.4 |
| `BECMG` | Ordered change; period normally &lt;2 h, never &gt;4 h (Rec) | App 5 §1.3.2 / A5-2 |
| `TEMPO` | Temporary fluctuations; each &lt;1 h, aggregate &lt;½ indicated period (Rec) | Same |
| `PROB30` / `PROB40` | Probability changeForecast; **only** 30 or 40; ≥50% → not PROB | App 5 §1.4 — PROB must not qualify BECMG or FM |
| `TL` | Period from forecast validity start → TL | #735 exceptional |
| `AT` | Represent as a time instant | #735 exceptional |

**Note:** Guidance METAR/SPECI trend section covers BECMG/TEMPO without TL/AT/FM for
*landing TREND* (nilReason missing/unknown on phenomenonTime). TAF change encoding
relies on #735 + Annex App 5 + FM 205 TAF req class — keep TREND vs TAF change
tables **separate** in lint.

**Gap:** no dedicated T2 accept/negative set yet; `TEMPO_PRESENT` today is METAR/SPECI-tagged only.

### T3 — TX/TN · CAVOK · NSC · NSW · VV///

| TAC | Encode | Lint |
|-----|--------|------|
| `TXnn/nnnnZ` + `TNnn/nnnnZ` | Paired max/min + occurrence times on **baseForecast only**; Annex may repeat a single extremum in both groups | Reject TX/TN on change groups |
| `CAVOK` | `cloudAndVisibilityOK=true`; omit vis / RVR / weather / cloud | Mutual exclusion vs those groups |
| `NSC` | Cloud nil `…/nothingOfOperationalSignificance` | Token valid when CAVOK inappropriate |
| `NSW` | Weather nil `…/nothingOfOperationalSignificance` | End of phenomena |
| `VV///` | **Omit** `verticalVisibility` with **no** nilReason (TAF-specific — differs from METAR/SPECI `notObservable`) | Do not invent nil on TAF VV/// |

### T4 — Goldens

- Expand `annex3_golden` (+ `iwxxm_us_golden`) TAF manifests beyond `taf_basic.tac` /
  `taf_us_altimeter`.
- Assert root `iwxxm:TAF` for pinned `iwxxm_version` (esp. 2025-2).
- Round-trip convert → `iwxxm-validate` (M-xsd / M-sch).
- Prefer official `taf-A5-*` examples as seeds; synthetic short cases for lint codes.

---

## Theme detail — SPECI (S1–S3)

### S1 — Exceptional rules (shared METAR/SPECI structure)

From Guidance METAR/SPECI + #734 (same table as METAR):

| TAC | Encode |
|-----|--------|
| `NIL` | Empty `observation` + `…/nil/missing` |
| `CAVOK` | `cloudAndVisibilityOK`; omit vis/RVR/wx/cloud |
| `NSC` / `NCD` | Cloud nil `nothingOfOperationalSignificance` / `notDetectedByAutoSystem` |
| `NOSIG` | Single nil `trendForecast` + `noSignificantChange` |
| `NSW` in trend | Forecast weather nil `nothingOfOperationalSignificance` |
| Present wx `//` / `VV///` | `notObservable` nils (**obs** path — not TAF VV/// omit rule) |
| Missing RVR | `missing` vs `notObservable` per sensor presence |
| `dddVddd` | Counter-clockwise then clockwise extremes |

**F15 baseline:** R1–R8 closed; SPECI negatives exist under
`packages/tac-validate/tests/fixtures/negative/speci/`. **Deepen:** accept fixtures +
encode fidelity for each exceptional row still thin vs #734 AC; no `runwayState`.

**Annex 3 (paywall):** SPECI **shall** App 3 §2.3.2 vs **Recommendation** §2.3.3 —
numeric engines stay citation-gated; lint may INFO/WARN with section cites only unless
licensed ruleset present.

**FMH-1 (US):** separate SPECI criteria §2.5.2 (SM/ft) — do **not** merge with App 3
tables; profile `iwxxm_us` only.

### S2 — Mis-classification

- Auto-detect / product-hint must not accept SPECI TAC as METAR (or reverse).
- Shared `metarSpeci` parse path OK; **report type** and IWXXM root must stay SPECI.
- TC-F20-006 owns adjacency negatives (extend F15 R7).

### S3 — Goldens

- Expand annex3 / iwxxm_us SPECI goldens; root `iwxxm:SPECI`.
- Round-trip XSD + Schematron.

---

## Theme detail — C1 (common)

From Guidance **All reports** + #735/#734 common table:

| Condition | IWXXM |
|-----------|-------|
| Normal / amended / corrected | `reportStatus` = `NORMAL` / `AMENDMENT` / `CORRECTION`; `reportStatus` + `permissibleUsage` required |
| Translation by another centre | Translated bulletin ID, reception time, centre, translation time |
| TAC incompletely understood | `translationFailedTAC` — do **not** distribute partial operational IWXXM |
| Horizontal geometry | 2-D CRS: `srsName`, `srsDimension="2"`, `axisLabels` |
| Coded weather / phenomenon | WMO code-list URI — not free-text abbreviation |
| Missing / unknown / N/A | `xsi:nil` + correct `nilReason` — never fabricate |
| Multi-report TAC bulletin | One IWXXM report object per TAC report |

Lint applies where TAC surface tokens exist (AMD/COR/NIL); CRS / translation-failed /
COLLECT packing may be convert-only with matrix note if lint N/A.

---

## Suggested registry tags (M1+)

Extend ADR-028 catalog with `tags` including `taf` and/or `speci` where product-specific.
Candidate codes (names illustrative — finalize in T1.2 / T3.2):

| Theme | Candidate codes |
|-------|-----------------|
| T1 | `TAF_NIL_REPORT`, `TAF_CNL_SHAPE`, `TAF_AMD_PRESENT`, `TAF_COR_PRESENT`, `INVALID_TAF_NIL`, `INVALID_TAF_CNL` |
| T2 | `TAF_FM_PRESENT`, `TAF_BECMG_PRESENT`, `TAF_TEMPO_PRESENT`, `TAF_PROB_PRESENT`, `INVALID_TAF_PROB`, `INVALID_TAF_CHANGE_ORDER` |
| T3 | `TAF_TX_TN_BASE_ONLY`, `TAF_CAVOK`, `TAF_NSC`, `TAF_NSW`, `TAF_VV_OMIT` |
| S1 deepen | Reuse / extend R8 + CAVOK/NSC/NCD/NOSIG/NSW/`//`/RVR/VRB codes with `speci` tag |
| S2 | `PRODUCT_MISCLASSIFIED` (or harden existing auto-detect errors) |
| C1 | Status / bulletin awareness codes where lintable |

Regenerate `ISSUE_CATALOG.md` (+ JSON) after registry edits; keep HTTP
`GET /api/v1/lint-issue-catalog` wire unchanged (FE filters at M5).

---

## Sample TAC seeds (synthetic — for fixtures)

Short synthetic cases only (not copyrighted Annex pages):

```text
TAF NIL
TAF AMD EHAM 120600Z 1206/1312 18010KT CAVOK=
TAF COR EGLL 011200Z 0112/0218 27015G25KT 9999 SCT020=
TAF KJFK 010000Z 0100/0206 00000KT CAVOK TX12/0118Z TN03/0208Z=
TAF LFPG 050500Z 0506/0612 20008KT 9999 BKN015 TEMPO 0508/0512 4000 -RA PROB40 0510/0512 2000 RADZ=
TAF CNL EHAM 120600Z 1206/1312=

SPECI EGLL 011230Z 27015KT 9999 SCT020 12/08 Q1013 NOSIG=
SPECI KJFK 011245Z AUTO 18005KT 1/2SM R04/2000FT FG VV/// 10/10 A2992=
SPECI NIL
```

Adapt into `packages/tac-validate/tests/fixtures/{accept,negative}/{taf,speci}/` and
`packages/tac2iwxxm/tests/fixtures/` goldens with expected codes / XML roots.

---

## Mapping → milestones

| Theme | Milestone tasks |
|-------|-----------------|
| Catalog + matrix link | T0.1 (this doc) · T0.2 |
| T1–T3 lint | T1.1–T1.6 |
| T4 goldens | T2.1–T2.3 |
| S1–S3 | T3.1–T3.6 |
| C1 + matrix close | T4.1–T4.4 |
| FE catalog TAF tags + smoke | T5.1–T5.7 |

---

## Gaps / kill-switch triggers

Raise AskQuestion (do **not** silently defer) if blocked on:

1. Licensed Annex 3 numeric SPECI/TAF threshold engines required for HARD AC (vs cite-only INFO).
2. Guidance silent on TAF FM/BECMG/TEMPO/PROB XML detail beyond #735 — need FM 205.adoc / SCH assert clarification.
3. TAF `VV///` omit-without-nil conflicts with shared cloud helper used for METAR/SPECI.
4. Any HARD theme undeliverable under Lean+build schedule.

---

## References (in-repo)

- [COVERAGE_MATRIX.md](../../../domain/rules/COVERAGE_MATRIX.md) §TAF / SPECI — F20
- [TAC_VALIDATION.md](../../../domain/TAC_VALIDATION.md) A5-1 / A3-2 checklists
- [RULE_SOURCE_URLS.md](../../../domain/rules/RULE_SOURCE_URLS.md)
- [aerodrome-quality.md](../../../context/aerodrome-quality.md)
- [execution-plan.md](./execution-plan.md)
