# National IWXXM Extension Schema Trees — Pinability Assessment

**Ticket:** [#1198](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1198)  
**Date:** 2026-09-16  
**Status:** Stage 0 recorded — **#1198 stays blocked**; no M6 vendor-sync PR  
**Corpus:** [Corpus: product §F7.w] [Corpus: product §M6] [Corpus: adr/ADR-038] [Corpus: domain-profiles]

## Bottom line

None of the eight target national aviation weather lines (`AU_BOM`, `BR_DECEA`, `HK_HKO`, `IN_IMD`, `JP_JMA`, `KR_KMA`, `NZ_CAA_MET`, `UK_METOFFICE`) can be shown to publish a public, downloadable national IWXXM *extension* XSD/Schematron tree analogous to US `iwxxm-us` or Canadian `iwxxm-ca`. Keep emitting WMO core `national_lines: ["*"]` and `national_residuals.awaiting_vendor_pins`. Do **not** invent pins or stub XSDs.

> **Critical transparency note.** This assessment was produced under a degraded research configuration: general web-search/web-fetch was unavailable, and a research-subagent budget was consumed by a failed init before searches ran. The only external verification available was one automated enrichment pass that also could not reach the web. This report **cannot present positively-verified live URLs** for any national schema and does **not** independently re-verify US/Canada precedents. It rests on (a) domain knowledge of the IWXXM/WMO/ICAO ecosystem, (b) the EMPIRIC2/TAC-to-IWXXM product corpus, and (c) that enrichment pass. Every claim that would normally require a live-fetched source is marked with confidence (H/M/L) and flagged where unverified. **No URLs, repos, or schemas were invented.** Before any pin decision, re-check “could-not-verify” items with a working web channel (Stage 1).

---

## TL;DR

- **No pin-ready national extension schema** located for any of the eight lines. Dominant IWXXM pattern: States exchange using unmodified WMO core; published country-specific XSD layers (US, Canada) are rare. (Confidence: Medium.)
- **#1198 stays blocked.** No `vendor/manifest.json` entry proposed — a pin without a verified upstream URL violates read-only / no-invention.
- **Disposition = defer + targeted outreach**, not “WMO-only forever.” UK Met Office, BOM, JMA, KMA may hold non-public artifacts obtainable by request.

---

## Key findings

1. **Default is WMO-core, not national extensions.** IWXXM (ICAO Annex 3 / `wmo-im/iwxxm`) allows conformance via core schemas alone. National extensions add collectives, identifiers, constrained code lists — few States publish them. Explains why only US/CA are solved and the other eight default to `["*"]`.

2. **Publishing MET data ≠ publishing an extension schema.** Open-data portals/APIs (REDEMET, data.gov.hk, data.kma.go.kr, Met Office DataHub, BOM FTP/API) distribute METAR/TAF/SIGMET *content*. None confirmed to expose a vendorable national IWXXM XSD/Schematron *tree*.

3. **Japan trap.** JMA `xml.kishou.go.jp` (JMX) is domestic weather/disaster XML — **not** aviation IWXXM. Do not treat as a national IWXXM extension. (Confidence: Medium.)

4. **No negative finding is airtight this pass.** Correct class for all eight: **“could not verify a public XSD this pass”**, not the stronger **“confirmed does not exist publicly.”**

5. **Product corpus confirms the operating model.** TAC→IWXXM validation is anchored on WMO core; national blocks are additive and gated on real pins (ADR-038 amend / F7.w residuals).

---

## Per-country table

| Line | National extension XSD located? | Publisher | Canonical URL | Version | License posture | Confidence | Notes |
|---|---|---|---|---|---|---|---|
| **AU_BOM** | Could not verify this pass | Bureau of Meteorology | None verified | n/a (WMO core) | BOM data terms; no schema license found | **M** | High-value outreach |
| **BR_DECEA** | Could not verify this pass | DECEA / REDEMET | None verified | n/a | REDEMET API terms (data) | **M** | Content API, not schema |
| **HK_HKO** | Could not verify this pass | Hong Kong Observatory | None verified | n/a | data.gov.hk terms | **M** | Product feeds only |
| **IN_IMD** | Could not verify this pass | India Meteorological Department | None verified | n/a | IMD terms | **L** | Opaque/credentialed portal |
| **JP_JMA** | Could not verify this pass | Japan Meteorological Agency | None verified | n/a | JMA terms | **M** | JMX ≠ aviation IWXXM |
| **KR_KMA** | Could not verify this pass | Korea Meteorological Administration | None verified | n/a | data.kma.go.kr terms | **L** | Products, not schema tree |
| **NZ_CAA_MET** | Could not verify this pass | MetService / CAA NZ | None verified | n/a | Commercial SOE / Crown | **L** | Credentialed aviation MET |
| **UK_METOFFICE** | Could not verify this pass | UK Met Office | None verified | n/a | Crown; OGL if released | **M** | Strong outreach target |

---

## Reference precedents (requester-supplied; not re-verified this pass)

- **Core:** `wmo-im/iwxxm` (e.g. 2025-2)  
- **US:** NWS `iwxxm-us` 3.0 tarball → `vendor/manifest.json` `iwxxm-us`  
- **CA:** ECCC datamart schema dir → `vendor/manifest.json` `iwxxm-ca`

### Proposed `vendor/manifest.json` entries

**None.** No target line is pin-ready.

Illustrative future shape only (do **not** commit until URL verified):

```jsonc
// ILLUSTRATIVE ONLY — not a real, resolvable source. Do not commit.
"iwxxm-<cc>": {
  "upstream_repo": "<verified org/repo>",
  "tag": "<verified git tag>",
  "maps_to_iwxxm_release": "2025-2",
  "license": "<verified license>",
  "namespace": "<verified xmlns from the XSD>"
}
```

### Path / version mismatches

- Keep `NATIONAL_VENDOR_EXPECTATIONS` dirs as empty skip targets — no rename while no upstream.
- Pre-guessed `3.0` segments are likely wrong in principle; real layers would track WMO dated releases (e.g. `2025-2`). Defer rename until a real upstream version string is known.
- Guessed `iwxxm-xx` prefixes are unverified — capture from real XSD at pin time.
- Miner: empty dirs → `awaiting_vendor_pins` (correct residual).

---

## Recommendations

### Stage 0 — Immediate (done this pass)

- Keep **#1198 blocked**. Record this report. Do **not** open an M6 vendor-sync PR. Keep all eight on WMO `["*"]` with `awaiting_vendor_pins`.

### Stage 1 — Re-verify with working web channel

Before any pin: GitHub org/repo search; `codes.wmo.int` for national namespaces; `wmo-im/iwxxm` wiki/docs for known national extensions; each NMS developer/schema page; regional (EUR / Asia-Pacific) shared bundles.  
**Threshold:** any resolvable, redistributable XSD/SCH tree → Stage 2 for that country.

### Stage 2 — M6 vendor-sync PR (only if Stage 1 finds a real source)

Pin mirroring `iwxxm-us`/`iwxxm-ca`, stable versioned URL/tag, true namespace + license, M6 sync, re-run `mine_conversion_schema_blocks.py`, reopen #1198 mine for those countries.  
**License gate:** MIT/Apache/CC-BY/OGL/PD OK; all-rights-reserved / no-license → request permission first; do not vendor.

### Stage 3 — Outreach (parallel if negative holds)

Ask: *“Do you publish a national IWXXM extension XSD/Schematron on WMO core? URL + license (redistribution)? If not public, may we obtain a copy for validation tooling?”*

1. UK Met Office (DataHub/DataPoint)  
2. Australia BOM  
3. JMA aviation (not JMX domestic feed team)  
4. KMA (`data.kma.go.kr`)  
5. DECEA/REDEMET  
6. HKO / data.gov.hk  
7. IMD aviation  
8. MetService NZ / CAA NZ  

Declare **“WMO-only forever”** for a line only after Stage 1 clean negative **and** Stage 3 confirmation. Until both: **defer**.

---

## Caveats

- Severe: no live web verification this pass — “could not verify” ≠ “confirmed absent.”  
- Precedent URLs are requester-supplied.  
- No fabricated sources.  
- JMA JMX false-positive risk.  
- License unknowns even if a schema surfaces.  
- Version-guess risk on `.../3.0` paths.  
- No changes to `vendor/schemas/*`, miner, Profile Builder, or promote in this pass.

---

## Decision log

| ID | Outcome |
|----|---------|
| D-EVPYL-R-11 | Research saved; #1198 remains blocked (2026-09-16) |
| D-EVPYL-R-12 | No M6 national pin PR; no invented XSDs |
| D-EVPYL-R-13 | Next: Stage 1 live web re-verify and/or Stage 3 outreach |
