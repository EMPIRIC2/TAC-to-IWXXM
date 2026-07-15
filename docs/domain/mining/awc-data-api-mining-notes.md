# Aviation Weather Center Data API — focused mining notes

**Status:** working notes (not normative). Verify against live OpenAPI.  
**Focus of this pass:** live TAC/IWXXM test fixtures · formats · rate limits · vs official WMO examples  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Local extracts (if any, gitignored):** none (HTML SPA + OpenAPI fetched ephemerally)

**Promote durable findings into:**

| Doc | Path |
|-----|------|
| Domain hub | [../README.md](../README.md) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |

| Item | Value |
|------|-------|
| Title | Aviation Weather Center (AWC) Data API |
| Publisher | NOAA / NWS Aviation Weather Center |
| Official landing | https://aviationweather.gov/data/api/ |
| OpenAPI | https://aviationweather.gov/data/schema/openapi.yaml |
| Pin / edition | API UI rev noted `v4.22` (footer); not an IWXXM package pin |
| Date mined | 2026-07-14 |
| Access | public HTTPS; rate-limited (100 req/min); custom User-Agent recommended; **no CORS** |
| Label | **informative** (live/recent operational data — not WMO/ICAO encode SoT) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Machine API for recent METAR/TAF (+ other aviation products) in **raw, JSON, GeoJSON, XML, IWXXM** | Replacement for official `schemas.wmo.int/…/examples/` golden pairs |
| Useful for F8 / integration / smoke against live US centre translation | Normative nilReason / Schematron authorship |
| Documents cache files for bulk pulls | Official COLLECT / AMHS filename SoT (use OPMET Guidelines) |

---

## Product × artifact matrix

| Product | TAC input | IWXXM / XML output | Official example / guidance | Gap vs GIFTs | Consumer |
|---------|-----------|--------------------|-----------------------------|--------------|----------|
| METAR | `/api/data/metar?format=raw` | `format=iwxxm` (ns `http://icao.int/iwxxm/2025-2`) | AWC OpenAPI; **not** WMO A3 examples | Live US RMK retained in TAC comment | live smoke · F8 |
| TAF | `/api/data/taf?format=raw` | `format=iwxxm` (OpenAPI) | same | — | live smoke |
| AIRMET (AK) | — | OpenAPI `JSONGeoIWXXM` | Alaska AIRMETs; CONUS = G-AIRMET | US domestic | optional |
| SIGMET | raw/JSON/XML | (**no** IWXXM in product table — XML only) | AWC SIGMET XML ≠ WMO SIGMET examples | — | not F6 golden |
| SPECI / TCA / VAA | not primary AWC Data API focus | — | use WMO examples | — | — |

---

## Key findings

### Endpoints and formats

- Base: `https://aviationweather.gov/api/data/{product}`
- Docs: SPA at `/data/api/`; machine spec at `/data/schema/openapi.yaml`
- METAR formats (OpenAPI `RawJSONGeoXMLIWXXM`): raw, json, geojson, xml, **iwxxm**
- Product table on landing: METAR / TAF list **IWXXM**; AIRMET (Alaska) lists IWXXM; SIGMET / G-AIRMET / PIREP do **not** claim IWXXM on the landing table

### Live sample (2026-07-14, KJFK METAR `format=iwxxm`)

- Namespace: `http://icao.int/iwxxm/2025-2` (aligns with pin **line**)
- `xsi:schemaLocation` pointed at **`http://schemas.wmo.int/iwxxm/2025-2RC1/iwxxm.xsd`** (RC1 path still published; prefer **`…/2025-2/`** for validate/cite)
- Metadata: `translationCentreDesignator="KKCI"`, `translationCentreName="NWS/AWC"`, `permissibleUsage="NON-OPERATIONAL"`
- TAC embedded in XML comment includes **US REMARKS** (`RMK AO2 …`) — relevant to `iwxxm_us` / FMH-1, not Annex 3 golden encode

### Smoke vs `iwxxm-validate` (2026-07-14 continue pass)

| Sample | Shape | Well-formed? | Package `validate(..., 2025-2)` | Notes |
|--------|-------|--------------|----------------------------------|-------|
| Official `metar-A3-1.xml` (control) | single `iwxxm:METAR` | yes | `ok=True` with **warnings only** | Engine currently **skips** strict XSD (GML import) and Schematron (`queryBinding=xslt2`) for 2025-2 |
| AWC METAR KJFK | **`collect:MeteorologicalBulletin`** wrapping `iwxxm:METAR` member(s) | yes (xlink declared on member) | same skip warnings → `ok=True` | Not a single-report document; COLLECT 1.2 schemaLocation |
| AWC TAF KJFK | single `iwxxm:TAF` | **no** | `ok=False` — `xlink:href` on `iwxxm:amount` **without** `xmlns:xlink` | Live feed defect; do not use as golden or SCH fixture until fixed |

**Conclusion:** AWC is useful for **live TAC** and for observing KKCI translation metadata / COLLECT wrapping; it is **not** a substitute for official examples. Full XSD+Schematron release-gate proof still requires official examples + an engine path that actually runs `xslt2` Schematron (current package logs skip).

### Local samples (gitignored)

`.local/reference/awc-data-api-samples/` — METAR COLLECT, TAF (malformed), official control copy.

### Operational constraints (from landing)

- ~15 days of history; max ~400 results/query; prefer `/data/cache/*.gz` for bulk
- Rate limit: 100 requests/minute; advise ≤1 req/min/thread for heavy use
- HTTP 204 = valid empty; 429 = rate limit

---

## Catalog paste rows

```text
### Aviation Weather Center Data API
- Publisher: NOAA / NWS AWC
- URL: https://aviationweather.gov/data/api/
- Stable concept pattern: https://aviationweather.gov/api/data/{metar|taf|…}?format={raw|json|iwxxm|…}
- Access: public (rate-limited; no CORS)
- Applies to: products=[METAR,TAF,(AIRMET AK)]; profiles=[iwxxm_us useful]; role=[conversion, iwxxm-validation] (fixtures only)
- Gap vs GIFTs: live multi-format including IWXXM; US REMARKS in TAC
- Consumer: live smoke / F8 — not CI golden SoT
- Label: informative
- Caveats: schemaLocation may cite 2025-2RC1; NON-OPERATIONAL permissibleUsage; not WMO official examples
```

---

## Domain-knowledge cross-check (required on full / refresh passes)

| Older claim (doc + date/edition) | This source finding | Action |
|----------------------------------|---------------------|--------|
| No AWC row in RULE_SOURCE_URLS | Public IWXXM-capable API for METAR/TAF | **Add** informative catalog row |
| Official examples = sole live IWXXM | AWC returns 2025-2 ns IWXXM from KKCI | Keep WMO examples as **golden**; AWC = optional live |
| ENHANCEMENTS.md mentioned aviationweather.gov tests | Confirmed OpenAPI + live iwxxm | Align citations to this dig / catalog |
| AWC IWXXM usable as SCH smoke | TAF missing `xmlns:xlink` (not well-formed); METAR wrapped in COLLECT; package skips xslt2 SCH | Caveat heavily; do **not** gate releases on AWC |
| Suggested “compare vs Schematron” | Engine skip for 2025-2 `xslt2` | Deferred pending SCH runner that executes pin Schematron |

---

## Implications for this repo

- **F6 / tac2iwxxm:** do not regress against AWC XML; encode vs official `.tac`/`.xml` + Guidance
- **tac-validate:** optional raw METAR/TAF feeds for US lint
- **iwxxm-validate:** optional live positive samples — expect translation-centre attrs + possible RC1 schemaLocation; still validate against **vendor** `2025-2`
- **Caveats / TBD:** do not treat AWC IWXXM as Annex 3 golden; watch RC1 vs final path drift

---

## Suggested next mining passes

1. ~~Compare one AWC IWXXM METAR vs vendored Schematron~~ — attempted 2026-07-14: package **skips** `xslt2` SCH; TAF not well-formed
2. When an `xslt2` Schematron runner exists, re-validate extracted METAR **member** XML (not COLLECT wrapper) against vendor pin
3. Re-fetch AWC TAF after confirming `xmlns:xlink` is restored upstream
