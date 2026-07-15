# FMH-1 (2019) — focused mining notes

**Status:** working notes (not normative). Verify against the official PDF / NWS registries.  
**Focus of this pass:** METAR/SPECI body + **RMK** coding (§12) · SPECI criteria (§2.5.2) · gap vs Annex 3 / GIFTs for profile `iwxxm_us`  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Local extracts (gitignored):** `.local/reference/fmh1-2019/`

**Promote durable findings into:**

| Doc | Path |
|-----|------|
| Domain hub | [../README.md](../README.md) |
| TAC validation | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |

| Item | Value |
|------|-------|
| Title | Federal Meteorological Handbook No. 1 — Surface Weather Observations and Reports |
| Publisher | OFCM / ICAMS (US Federal) |
| Official landing | <https://www.icams-portal.gov/resources/ofcm/fmh/FMH1/fmh1_2019.pdf> · index <https://www.icams-portal.gov/resources/ofcm/fmh/allfmh2.htm> |
| Pin / edition | **2019** (PDF last-modified ~2021-01-15 on CDN) |
| Date mined | 2026-07-14 |
| Access | **public** PDF |
| Label | **normative** (US national surface-obs / METAR coding) for profile `iwxxm_us` |
| Pages | 101 |
| Local text | `.local/reference/fmh1-2019/fulltext.txt` |
| Focus extract | `.local/reference/fmh1-2019/extracts/ch12_coding_remarks.txt` (PDF pp. 60–90) |
| Vendor pin (runtime IWXXM) | `vendor/manifest.json` → **v2025-2** (+ `iwxxm-us` **3.0** for extensions) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| US **METAR/SPECI** body order + **RMK** grammar (Ch.12) | ICAO Annex 3 international SARPs SoT |
| US **SPECI** issue criteria (§2.5.2) in statute miles / feet | Identical SPECI thresholds to Annex 3 App 3 §2.3 |
| Machine companions expected at `codes.nws.noaa.gov/FMH-1` (probe timed out 2026-07-14) | IWXXM nilReason / XSD encode cookbook |
| Gap baseline that explains GIFTs stripping REMARKS | Encode SoT for `annex3` profile |

---

## Product × artifact matrix

| Product | Input (TAC / …) | Output (IWXXM / …) | Official example or register | Gap vs GIFTs | Consumer |
|---------|-----------------|--------------------|------------------------------|--------------|----------|
| METAR (US) | Body §12.6 + RMK §12.7 | Body → annex3-like encode; **RMK → `iwxxm-us` `extension`** | FMH-1 + iwxxm-us examples | GIFTs stripped RMK | `tac-validate` `iwxxm_us`, `tac2iwxxm` |
| SPECI (US) | Same + §2.5.2 criteria | same | FMH-1 | same | same |
| TAF / SIGMET / … | — | — | not in FMH-1 | Out of scope | — |

---

## Key findings

### Report structure (§12.4–12.6)

- Body order (US): type → CCCC → time → AUTO/COR → wind **KT** → vis **SM** → RVR **FT** → weather → sky (SKC/CLR) → T/Td → altimeter **Axxxx**.
- Missing element → **omit group and preceding space** (§12.5) — differs from Annex 3/WMO use of `/` placeholders that map to IWXXM nilReasons.
- SPECI at scheduled METAR time → still coded as SPECI (§12.6.1).

### Remarks (§12.7) — do not strip

Two categories after `RMK`:

1. **§12.7.1 Automated / manual / plain language** (inventory includes): volcanic eruptions; tornadic B/E; **AO1/AO2**; PK WND; WSHFT; TWR/SFC VIS; variable/sector VIS; lightning; precip/TS begin-end; CIG variable; PRESRR/PRESFR; **SLPppp / SLPNO**; NOSPECI; SNINCR; …
2. **§12.7.2 Additive / maintenance:** Prrrr, 6/7 precip, snow depth, **TsnTTT…** hourly T/Td to 0.1 °C, 1/2/4 max-min, 5appp tendency, ice accretion, sensor status, **`$` maintenance**.

`RMK` omitted only when there are no remarks.

### SPECI criteria (§2.5.2) vs Annex 3

US list uses **statute miles** / **feet** thresholds. Full paraphrase table promoted to
[TAC_VALIDATION.md](../TAC_VALIDATION.md) §US SPECI issue criteria (wind shift 45°/15 min/10 kt;
vis 3/2/1 mi; RVR 2400 ft; tornado; TS; precip families; squalls; ceiling 3000…500 ft; …).

**Do not merge** with Annex 3 App 3 §2.3 shall/Rec tables (metres) — parallel but distinct
([icao-annex-3 dig](./icao-annex-3-mining-notes.md)).

### Units / national differences (lint hints)

| Topic | FMH-1 (US) | Annex 3 / IWXXM annex3 |
|-------|------------|-------------------------|
| Visibility | statute miles | metres |
| RVR | feet | metres |
| Wind | KT | m·s⁻¹ or KT per SARP/practice |
| Altimeter | inches `Axxxx` | QNH hPa |
| Clear sky | SKC / CLR | NCD/NSC/CAVOK patterns |
| Missing | omit group | often `/` → nilReason |

Encode national extras only under **`iwxxm-us` extension** — not invent ICAO-namespace elements ([IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md)).

### NWS registry

`https://codes.nws.noaa.gov/FMH-1` — **timed out** this pass (0 bytes / 15s). Keep catalog URL; retry later for machine tables.

---

## Catalog paste rows

```text
### Federal Meteorological Handbook No. 1 (FMH-1) — 2019
- Publisher: OFCM / ICAMS
- URL: https://www.icams-portal.gov/resources/ofcm/fmh/FMH1/fmh1_2019.pdf
- Access: public
- Applies to: products=[METAR,SPECI]; profiles=[iwxxm_us]; role=[validation, conversion]
- Gap vs GIFTs: full RMK §12.7 (AO1/AO2, SLP, additive T, $) — GIFTs stripped REMARKS
- Consumer: tac-validate | tac2iwxxm | UI-decode
- Label: normative (US national)
- Caveats: not Annex 3 SoT; SPECI thresholds ≠ App 3; body missing-data omit ≠ / nilReasons
- Mined: 2026-07-14 · notes mining/fmh1-2019-mining-notes.md
```

---

## Domain-knowledge cross-check

| Older claim | This pass | Action |
|-------------|-----------|--------|
| US REMARKS gap = cite URL only | Ch.12 REMARKS inventory + body/RMK split mined | **Promoted** lint keep-list + iwxxm-us element map → TAC_VALIDATION / IWXXM_CONVERSION |
| SPECI thresholds unified | FMH US miles/feet ≠ Annex 3 metres | Keep separate rule tables by profile |
| Missing data → always `/` | FMH omits missing groups | Profile-aware TAC lint |
| NWS FMH-1 registry always reachable | Timeout 2026-07-14 | Caveat catalog |

---

## Implications for this repo

- **`tac-validate` `iwxxm_us`:** retain RMK; validate AO1/AO2 etc. against FMH-1 + NWS tables when registry available; separate SPECI criteria path.
- **`tac2iwxxm`:** map US body analogous to annex3 where shared; put RMK/additive into **iwxxm-us extension**; never drop RMK silently (ADR-014 / GIFTs gap).
- **`iwxxm-validate`:** combined WMO + iwxxm-us catalogs when profile = US.
- **F7 / UI:** explain statute-mile body + REMARKS as US national, not Annex 3.

---

## Suggested next mining passes

1. Retry `codes.nws.noaa.gov/FMH-1` machine tables when reachable
2. Cross-walk AWC live TAC REMARKS samples ↔ §12.7 inventory
3. ~~iwxxm-us 3.0 element coverage for RMK~~ — **done** via vendored `metarSpeci.xsd` map in canonicals (example XML dir not in vendor snapshot)
