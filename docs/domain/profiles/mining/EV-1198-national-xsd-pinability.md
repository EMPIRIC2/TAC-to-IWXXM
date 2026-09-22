# National IWXXM Extension Schema Trees — Pinability Assessment

**Ticket:** [#1198](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1198)  
**Dates:** Stage 0 2026-09-16 · **Stage 1 live web re-verify 2026-09-16**  
**Session:** `EV-1198-stage1-national-xsd-web-reverify`  
**Status:** Stage 1 complete — **#1198 stays blocked for Conversion mining**; **AU = partial candidate (license + scope gate)**; no M6 vendor-sync PR opened this pass  
**Corpus:** [Corpus: product §F7.w] [Corpus: product §M6] [Corpus: adr/ADR-038] [Corpus: domain-profiles]

## Bottom line

> **Stage 0 note:** An earlier pass (same day) ran under a degraded web channel and classified all eight as “could not verify.” Stage 1 below supersedes that pass with live fetches.

Live web verification (2026-09-16) confirms:

1. **No full national extension tree** analogous to US `iwxxm-us` / CA `iwxxm-ca` was found for BR/HK/IN/JP/KR/NZ/UK.
2. **Australia (BOM) publishes a real, downloadable TAF-only national extension** (`AU-TAF` / `iwxxm-au` 1.0) via the ICAO WG-MIE / EUR DMG Global Extension Repository — **not** a multi-product national schema tree.
3. **UK Met Office** lists an experimental Colour State extension in its codes registry, but the **canonical XSD URL returns HTTP 404** — not pin-ready.
4. Keep emitting WMO core `national_lines: ["*"]` and `national_residuals.awaiting_vendor_pins` for all eight lines until a licensed, version-aligned M6 pin is approved.
5. Do **not** invent pins or stub XSDs. Stage 3 national-office outreach remains out of scope for the operator this cycle.

---

## Stage 1 method (live channel)

Checked:

| Probe | Result |
|-------|--------|
| ICAO/EUR Global Extension Repository | `https://eur-rodex.austrocontrol.at/IWXXM-ext.php` — lists **AU-TAF** + FR MFLocalReport only |
| AU zip | `https://eur-rodex.austrocontrol.at/IWXXM-Files/taf.zip` → **HTTP 200**, contains `taf.xsd` |
| Met Office IWXXM extensions register | Registry entry for `ukColourStateExtension.xsd` (**experimental**); dereference → **HTTP 404** |
| GitHub `iwxxm-{jp,kr,br,hk,nz,in,uk}` style repos | No national extension trees located |
| `schemas.wmo.int/iwxxm/2025-2/` | WMO **core** only |
| US/CA precedent URLs (re-verify) | US tarball **200**; CA schema dir **200** |
| JMA `xml.kishou.go.jp` | Domestic JMX — **not** aviation IWXXM (trap confirmed) |
| KMA ICAO IP (2026) | IWXXM exchange plans; **no** national XSD published in that paper |

Evidence (session): `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-1198-stage1-national-xsd-web-reverify/evidence/stage1-2026-09-16/`

---

## TL;DR

| Line | Stage 1 class | Pin for M6? |
|------|---------------|-------------|
| **AU_BOM** | **Partial candidate** — public TAF-only XSD (`iwxxm-au` 1.0) | **Not yet** — license unknown; leaf-only; related IWXXM **3.0.1** not 2025-2 |
| **BR_DECEA** | No public XSD found (live-checked) | No |
| **HK_HKO** | No public XSD found (live-checked) | No |
| **IN_IMD** | No public XSD found (live-checked; portal opaque) | No |
| **JP_JMA** | No aviation IWXXM extension XSD; JMX ≠ IWXXM | No |
| **KR_KMA** | No public extension XSD (OPMET/IWXXM ops papers only) | No |
| **NZ_CAA_MET** | No public XSD found (live-checked) | No |
| **UK_METOFFICE** | Registry lists Colour State ext; **XSD URL 404** | No |

**Disposition:** remain **defer / blocked** for #1198 Conversion mining. Optional follow-on: AskQuestion for **AU Stage 2** only after license + TAF-only scope acceptance.

---

## Key findings

1. **Global Extension Repository is the right index.** WG-MIE-backed EUR DMG page hosts downloadable State extensions. As of Stage 1 it contains only France + Australia — confirming national XSDs are rare and catalogued centrally when shared.

2. **AU-TAF is real but narrow.** Namespace `http://www.bom.gov.au/aviation/iwxxm-au/1.0`, prefix `iwxxm-au`, zip sha256 `5b16e2d09d1854c27f51abdb62b791a4d15ff5199cd47108bee4add5855cea32`. Covers INTER/TEMPO interpretation, QNH, remarks-related TAF extension types — **not** METAR/SPECI/SIGMET national packs. Related IWXXM leaf version **3.0.1**.

3. **UK is a registry ghost.** Met Office Codes Registry documents Colour State (military aerodrome) as experimental; the delegated XSD resource does not resolve. Cannot pin a 404.

4. **US/CA precedents re-verified reachable** at the URLs already in `vendor/manifest.json` (shape templates remain valid).

5. **Guessed `vendor/.../iwxxm-au/3.0` path remains wrong in principle** — real AU namespace is **1.0** under BOM URI; do not rename placeholders until a licensed pin is approved.

---

## Per-country table (Stage 1)

| Line | Stage 1 class | Publisher | Canonical URL | Version | License | Conf. | Notes |
|---|---|---|---|---|---|---|---|
| **AU_BOM** | Partial candidate (TAF-only XSD) | BOM via EUR DMG | `https://eur-rodex.austrocontrol.at/IWXXM-Files/taf.zip` | ext **1.0** / related IWXXM **3.0.1** | **Not stated** in XSD/zip | **H** | `targetNamespace` `http://www.bom.gov.au/aviation/iwxxm-au/1.0` |
| **BR_DECEA** | No public XSD found | DECEA / REDEMET | — | — | — | **M** | Content APIs ≠ schema |
| **HK_HKO** | No public XSD found | HKO | — | — | — | **M** | Open data = products |
| **IN_IMD** | No public XSD found | IMD | — | — | — | **L** | Opaque/credentialed |
| **JP_JMA** | No public XSD found | JMA | — | — | — | **H** | JMX domestic XML trap |
| **KR_KMA** | No public XSD found | KMA AMO | — | — | — | **M** | IWXXM ops; no ext XSD |
| **NZ_CAA_MET** | No public XSD found | MetService / CAA | — | — | — | **L** | Commercial/credentialed |
| **UK_METOFFICE** | Registry only; XSD 404 | UK Met Office | register OK; XSD **404** | experimental Colour State | Crown / unknown | **H** | Not pin-ready |

---

## Reference precedents (re-verified Stage 1)

- **Core:** `wmo-im/iwxxm` tag `v2025-2` / `https://schemas.wmo.int/iwxxm/2025-2/`
- **US:** `https://nws.weather.gov/schemas/iwxxm-us/3.0/iwxxm-us-3.0-schemas.tgz` → HTTP 200
- **CA:** `https://dd.weather.gc.ca/today/aviation/iwxxm/schema/` → HTTP 200

### Proposed `vendor/manifest.json` entries

**None committed this pass.**

Illustrative **future** AU entry (do **not** commit until license + scope AskQuestion):

```jsonc
// ILLUSTRATIVE ONLY — license gate open; TAF-only; IWXXM 3.0.1-related.
"iwxxm-au": {
  "source_url": "https://eur-rodex.austrocontrol.at/IWXXM-Files/taf.zip",
  "tag": "1.0",
  "maps_to_iwxxm_release": "3.0.1",  // NOT 2025-2 — explicit mismatch
  "license": "<REQUIRED before pin>",
  "namespace": "http://www.bom.gov.au/aviation/iwxxm-au/1.0"
}
```

---

## Recommendations

### Stage 0 — done (prior)

Keep #1198 blocked; no invented XSDs.

### Stage 1 — done (this session)

Live re-verify complete; report + decisions + issue updated.

### Stage 2 — conditional (AU only)

Open Build **only after** AskQuestion covering:

1. Accept **TAF-only** national extension (not full `iwxxm-us`-class tree) for mining / Profile Builder?
2. License / redistribution into MIT monorepo (BOM / Austro Control hosting — confirm terms)?
3. Pin under which local path/version (real **1.0**, not guessed `3.0`)?
4. Align miner `NATIONAL_VENDOR_EXPECTATIONS` to BOM namespace vs keep awaiting fuller pack?

Default recommendation until those are answered: **do not open M6 PR**.

### Stage 3 — outreach

Still the path for BR/HK/IN/JP/KR/NZ/UK (and UK XSD repair). **Operator cannot perform outreach this cycle** — leave deferred.

**WMO-only forever:** still requires Stage 1 clean negative **and** Stage 3 confirmation — not declared.

---

## Caveats

- AU zip is a **single** `taf.xsd` (name collides conceptually with WMO `taf.xsd` — vendor path must disambiguate).
- No Schematron shipped in the AU zip.
- UK registry ≠ downloadable schema.
- License silence ≠ permission to vendor.
- Stage 3 unavailable this cycle.

---

## Decision log

| ID | Outcome |
|----|---------|
| D-EVPYL-R-11..13 | Stage 0 (prior) |
| D-EV1198-S1-01 | Stage 1 live web re-verify completed 2026-09-16 |
| D-EV1198-S1-02 | AU-TAF verified downloadable; namespace `iwxxm-au` 1.0; TAF-only |
| D-EV1198-S1-03 | UK Colour State registry found; XSD URL 404 — not pin-ready |
| D-EV1198-S1-04 | BR/HK/IN/JP/KR/NZ — no public extension XSD found this pass |
| D-EV1198-S1-05 | #1198 remains blocked for Conversion mining; no M6 PR |
| D-EV1198-S1-06 | US/CA precedent URLs re-verified HTTP 200 |
| D-EV1198-S1-07 | Stage 3 outreach deferred (operator constraint) |
| D-EV1198-S1-08 | AU Stage 2 requires separate AskQuestion (license + TAF-only scope) |
