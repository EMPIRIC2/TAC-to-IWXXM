# wmo-im/iwxxm-translation — parity backlog dig (2026-07-30)

Transitory dig — **not** standing SoT. README: **no official WMO/ICAO status**.

**Source:** IWXXM Translation Suite  
**URL:** https://github.com/wmo-im/iwxxm-translation  
**Vendor mirror:** `vendor/schemas/iwxxm-translation/` (`LATEST_EXAMPLE` → `Amd79-80-2023`, `IWXXM_VERSION` → **2023-1**)  
**Label:** **informative** / normative-examples (fixtures only)  
**Mined:** 2026-07-30  
**Ticket:** [#797](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/797)  
**Prior:** [wmo-im-tier-a-mining-notes.md](./wmo-im-tier-a-mining-notes.md) §3 · [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) P2 fixtures

## Focus

What to adjust in `tac2iwxxm` / `tac-validate` / `iwxxm-validate` golden policy using this suite — cross-linked from APAC FAQ §3.2 / §8.7.

## Suite shape (master, 2026-07-30)

| Amendment folder | Role | Products present |
|------------------|------|------------------|
| Amd77-2016 | historical | small set |
| Amd78-2018 | historical | metar-heavy |
| Amd79-80-2021 | historical | metar/taf/vaa/tca |
| **Amd79-80-2023** (= `LATEST_EXAMPLE`) | current suite tip | **metar/** 34 pairs (14 METAR + 20 SPECI), **TAF** (~7), **VAA** (~4), **TCA** (~4) |
| Root `metar/` `taf/` … | **absent** on tip (all under Amd*) | — |

**Explicitly absent:** dedicated SIGMET / AIRMET / SWX trees. **SPECI** lives under `metar/` (20 `SPECI` + 14 `METAR` TAC files at tip — not a separate product folder).

Fixture contract (README):

- Expect **exact** TAC↔IWXXM translation modulo whitespace/newlines.
- XML comment embeds TAC for illustration only — **not** operational practice (matches APAC FAQ §4.1).
- ICAO-compliant TAC only; reject regional/broken TAC that cannot map to IWXXM.

### NSC / missing-WX / nil fixtures useful for #797 P0 (suite TAC → re-encode 2025-2)

| Fixture (Amd79-80-2023) | TAC cue | Suite XML (2023-1) pattern |
|-------------------------|---------|----------------------------|
| `metar/EFHK-290020Z` | SPECI … **NSC** … NOSIG | `cloud` empty + `common/nil/nothingOfOperationalSignificance`; trend `noSignificantChange` |
| `taf/OIZC-131130Z` | base/TEMPO/BECMG **NSC** | repeated empty `cloud` + same nil |
| `taf/SARP-131100Z` / `SARP-131251Z` | PROB … BR **NSC** | NSC after weather (not layered cloud) |
| `metar/LTCN-282350Z` / `EDDH-290020Z` | no WX group | `weather` + `nothingOfOperationalSignificance` |
| `metar/CWFD-290000Z` | AUTO `//` WX | `presentWeather` + `notObservable` (+ other AUTO nils) |
| `metar/ENFB-282350Z` | AUTO `////` vis | `visibility` / dewpoint / SST `notObservable` |
| VAA `FVAU03ADRM-0424` | colour RED | **`49-2/AviationColourCode/RED`** — suite year lag; pin 2025-2 VAA should prefer **`iwxxm/`** colour set |

Confirmed suite xmlns: `http://icao.int/iwxxm/2023-1` (e.g. EFHK SPECI).

### `MetarSpeciTestCases.txt` / `TAFTestCases.txt` (ACCEPT catalog — not REJECT list)

Both files are **feature annotations** for included fixtures (all are ICAO-compliant ACCEPT examples). Highlights mapped to #797 seeds:

| Note (suite) | Fixture | Encode cue |
|--------------|---------|------------|
| “No significant cloud” | `EFHK-290020Z` | NSC → empty cloud + `nothingOfOperationalSignificance` |
| “No significant weather in TEMPO” | `EDDH-290020Z` | NSW / empty weather nil |
| “Missing … current weather …” | `CWFD-290000Z`, `EHJR-…` | AUTO `//` → `notObservable` / `missing` |
| “CAVOK” | `EKCH-…`, TAF `SARP-…` | `@cloudAndVisibilityOK` path |
| TAF “No significant cloud forecast” | `OIZC-131130Z` | NSC across base/change groups |
| TAF NIL / CNL / AMD / COR | `DAOY`, `EHLW`, `SARP-131251`, `MGGT` | reportStatus / NIL shell |
| Bulletin id artifact | all METAR/SPECI | `translatedBulletinID=S[A\|P]XX99XXXX260000` — **test artifact**; ops should use real AHL |

No REJECT corpus in these tip folders — regional/broken TAC are excluded by README policy, not listed.

### Official pin `*-translation-failed.*` vs FAQ §8.6 / Guidelines §5.3.3

Under `vendor/schemas/iwxxm/IWXXM/examples/` (2025-2):

| Example | Root | Shared quarantine attrs observed |
|---------|------|----------------------------------|
| `metar-translation-failed` | `METAR` | `reportStatus=NORMAL`, `permissibleUsage=OPERATIONAL`, `@translationFailedTAC`, `translationCentreDesignator/Name`, `translationTime`, `translatedBulletinID`, `translatedBulletinReceptionTime` |
| `taf-translation-failed` | `TAF` | same |
| `airmet-translation-failed` | `AIRMET` | same |
| `va-advisory-translation-failed` | `VolcanicAshAdvisory` | same |
| `tc-advisory-translation-failed` | `TropicalCycloneAdvisory` | same |
| `spacewx-translation-failed` | `SpaceWeatherAdvisory` | same |
| `sigmet-translation-failed-collect` | COLLECT wrap | failed SIGMET **inside** collect member + same translation attrs |

Aligns with APAC FAQ §8.6 (failed → `translationFailedTAC`) and OPMET Guidelines §5.3.3 (product shell + original TAC). Fictional centre `YUZZ` / bulletin id `TTAAiiCCCYYGGgg` match PPT-02 workshop placeholders — **examples**, not production IDs. FAQ §14.5 still gates when to emit centre attrs (cross-State only); official failed examples always show them because they model a translation centre.

## Gaps vs this repo

| Gap | Detail | Adjustment |
|-----|--------|------------|
| Schema year | Suite tip is **2023-1**; our pin is **2025-2** | Structure / semantic compare + SCH on **re-encoded** 2025-2 — do **not** require XML byte-match to 2023-1 fixtures |
| Product coverage | No SIGMET/AIRMET in translation suite; SPECI under `metar/` | Keep official `schemas.wmo.int/…/examples/` as P0 for SIGMET/AIRMET; SPECI P2 TAC from suite OK |
| VAA colour href family | Suite tip still emits `49-2/AviationColourCode/…` | Expect **href rewrite** under 2025-2 encode — another reason byte-match fails |
| Historical failures | `docs/ARCHIVE/.../live-test-failures/*Amd79*` (~34 cases) show namespace/schemaLocation/translationCentre drift when comparing suite XML to live encode | Formalize “informative P2” harness: TAC in → our IWXXM out → XSD+SCH; optional tree-diff ignoring gml:id / translation* / issueTime clock |
| FAQ citation | FAQ §8.7 still points here for translator validation | Wire suite TAC as **accept** inputs; prefer official examples for SCH goldens |

## Product × artifact matrix

| Product | TAC input artifact | IWXXM output (suite tip) | Official example / guidance | Gap vs GIFTs | Consumer |
|---------|-------------------|--------------------------|-----------------------------|--------------|----------|
| METAR | `Amd79-80-2023/metar/*.tac` (14 METAR + shared folder) | paired `*.xml` (**2023-1**) | FAQ §8.7; Guidance | Regional METARs beyond GIFTs | P2 convert→2025-2 + SCH |
| SPECI | Same `metar/` folder (20 SPECI TACs) | paired XML 2023-1 | official `speci-A3-2` | NSC example EFHK | P2 TAC + P0 official SCH |
| TAF | `…/taf/*.tac` (~7) | paired XML 2023-1 | FAQ §8.7 | Outside GIFTs | P2 |
| VAA | `…/volcanic-ash-advisory/*.tac` (~4) | paired XML 2023-1 | FAQ §8.7 | Outside GIFTs | P2 |
| TCA | `…/tropical-cyclone-advisory/*.tac` (~4) | paired XML 2023-1 | FAQ §8.7 | Outside GIFTs | P2 |
| SIGMET / AIRMET | **absent** | — | `schemas.wmo.int/…/examples/` | Outside GIFTs | **P0 official only** |

## Catalog paste rows

```text
### iwxxm-translation parity policy (2026-07-30)
- Publisher: WMO TT-AvXML (convenience repo)
- URL: https://github.com/wmo-im/iwxxm-translation
- Access: public; vendor/schemas/iwxxm-translation/
- Applies to: products=[METAR,SPECI,TAF,VAA,TCA]; profiles=[annex3]; role=[conversion,iwxxm-validation]
- Gap vs GIFTs: extra ICAO-compliant pairs; SPECI under metar/; no SIGMET/AIRMET trees
- Consumer: tac2iwxxm (P2) | iwxxm-validate (informative)
- Label: informative
- Caveats: LATEST=Amd79-80-2023 / IWXXM 2023-1; no byte-match to 2025-2 encode; suite VAA colour still 49-2/; README disclaims official status
- Mined: 2026-07-30 · #797 · detail mining/iwxxm-translation-parity-mining-notes.md
```

## Domain-knowledge cross-check

| Older claim | This pass | Action |
|-------------|-----------|--------|
| Tier A: use translation fixtures as goldens without year caveat | Suite XML = **2023-1**; pin = **2025-2** | Document no byte-match (promoted); caveat Tier A §3 |
| FAQ §8.7 “try with your translator” | Still valid for **TAC accept** inputs | Keep; clarify SCH goldens = official examples |
| “SPECI only in notes” | 20 SPECI TACs under `metar/` | Correct product matrix |
| Historical ARCHIVE live-test “PASS” vs expected 2023-1 XML | Expected namespace ≠ actual 2025-2; VAA colour still `49-2/` | Do not revive byte-diff as release gate |

## Implications for this repo

- **F6 / tac2iwxxm:** Optional P2 harness: suite TAC → encode 2025-2 → XSD+SCH (#797); seed with EFHK/OIZC NSC + CWFD/LTCN missing-WX rows above.
- **tac-validate:** Suite TAC as annex3 accept shapes where ICAO-compliant (incl. SPECI under `metar/`).
- **iwxxm-validate:** Do not treat suite XML as pin SCH goldens; expect VAA colour URI family shift `49-2` → `iwxxm` under pin.
- **Caveats / TBD:** No SIGMET/AIRMET expansion expected from this repo alone.

## Suggested next mining passes

1. ~~NSC / missing WX inventory~~ — **done**.
2. ~~Skim MetarSpeciTestCases / TAFTestCases~~ — **done** (ACCEPT annotations only).
3. ~~Diff official `*-translation-failed*` vs FAQ/Guidelines~~ — **done** (attr matrix above; promote quarantine field list).
4. When upstream adds Amd for Annex 3 post-2023, re-check `LATEST_EXAMPLE` vs vendor pin.

## Promotion checklist

- [x] Document “no byte-match to 2023-1 XML” in `IWXXM_CONVERSION` / `IWXXM_VALIDATION` / `COVERAGE_MATRIX`
- [x] Product matrix + cross-check + implications (this continue)
- [x] NSC / missing-WX fixture seeds listed for #797
- [x] TestCases.txt + official translation-failed attr matrix documented
- [ ] Add automated P2 informative convert suite — **#797** (engine)
- [x] Mining index updated
