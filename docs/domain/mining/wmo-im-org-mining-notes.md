# wmo-im GitHub org — focused mining notes

**Status:** working notes (not normative). Verify against official registry / schemas.  
**Focus of this pass:** org-wide survey — which repos matter for Annex 3 / IWXXM data, TAC validation, conversion, IWXXM validation  
**Ticket:** discovery (pairs with [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719) catalog)  
**Org:** https://github.com/wmo-im (~103 public repos as of 2026-07-14)

**Standing catalog:**

| Doc | Path |
|-----|------|
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Companion (validation) | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| Companion (creation) | [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| Companion (schema val) | [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |

| Item | Value |
|------|-------|
| Title | WMO Information Management (`wmo-im`) org review |
| Publisher | WMO (community GitHub org) |
| Official landing | https://github.com/wmo-im |
| Pin / edition | Runtime: `vendor/manifest.json` → iwxxm **v2025-2**, iwxxm-codelists **49-2** |
| Date mined | 2026-07-14 |
| Access | public |
| Label | mixed (see tiers below) |
| Local Tier A clones | `.local/reference/wmo-im-tier-a/` — deep mine: [wmo-im-tier-a-mining-notes.md](./wmo-im-tier-a-mining-notes.md) |
| Local Tier B clones | `.local/reference/wmo-im-tier-b/` — deep mine: [wmo-im-tier-b-mining-notes.md](./wmo-im-tier-b-mining-notes.md) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Org that hosts **machine SoT** for IWXXM XSD/Schematron, 49-2 codelists RDF/CSV, UML modelling, and extra TAC↔IWXXM fixtures | A substitute for **ICAO Annex 3** / Doc 8896 / Doc 10003 (those remain paywalled store docs) |
| Useful entry points for WIS2 **aviation publish / topic** guidance (exchange, not TAC grammar) | Home of METAR/TAF/SIGMET **TAC FM templates** (those live in WMO-No. 306 Vol I.1 + Annex 3) |
| Historical COLLECT / SAF / METCE lineage still referenced by older package lines | Runtime encode/validate pin — use vendored `iwxxm` tag, not untagged historical repos |

---

## Tier ranking (Annex 3 + IWXXM roles)

### Tier A — primary (already vendored / catalogued)

| Repo | Label | Role | Why useful | Pin |
|------|-------|------|------------|-----|
| [wmo-im/iwxxm](https://github.com/wmo-im/iwxxm) | normative-schema (+ examples, conversion notes, embedded COLLECT) | `conversion`, `iwxxm-validation`, `bulletin` | XSD + Schematron + official examples + `TAC-to-XML-Guidance.txt`; topics include `annex-iii`; publishes to `schemas.wmo.int` | **v2025-2** |
| [wmo-im/iwxxm-codelists](https://github.com/wmo-im/iwxxm-codelists) | normative-vocabulary | `conversion`, `iwxxm-validation` | CSV/TTL for `codes.wmo.int/49-2/*` and related IWXXM registers; feeds registry | **49-2** |
| [wmo-im/iwxxm-modelling](https://github.com/wmo-im/iwxxm-modelling) | informative (tooling) | design only | UML → XSD/SCH generation; cite **published** `iwxxm` tag for runtime | **v2025-2** |
| [wmo-im/iwxxm-translation](https://github.com/wmo-im/iwxxm-translation) | **informative** | fixtures | Extra Annex 3 amendment–tagged TAC/XML pairs; README: **no official WMO/ICAO status** | `master` |

**Inside `iwxxm` (do not treat as separate pin):**

- `IWXXM/examples/` — normative-examples + `TAC-to-XML-Guidance.txt`
- `IWXXM/*.xsd` + `IWXXM/rule/*.sch` — runtime validate
- `externalSchema/schemas.wmo.int/collect/` — COLLECT bulletin schemas (use this over stale `wmo-im/collect`)
- `documentation/manual/FM205.adoc` — working FM 205 text tied to schema line (prose; Manual on Codes PDF still the formal publish for I.3)

### Tier B — secondary (useful for exchange / lineage / parallel vocab)

| Repo | Label | Role | Why useful | Caveat |
|------|-------|------|------------|--------|
| [wmo-im/collect](https://github.com/wmo-im/collect) | historical / normative-schema lineage | `bulletin` | Original Feature Collection / bulletin packaging model (AFS/WIS bulletin emulation) | Last meaningful commit **2017**; **prefer** collect XSD shipped under `iwxxm` `externalSchema` for the active pin |
| [wmo-im/wis2-cookbook](https://github.com/wmo-im/wis2-cookbook) | informative | `bulletin` / ops | `publishing-aviation-data.adoc` cites Annex 3 use-rights + IWXXM on WIS2 | Not TAC validation SoT |
| [wmo-im/wis2-topic-hierarchy](https://github.com/wmo-im/wis2-topic-hierarchy) | normative-exchange (WIS2 topics) | F8 / ingest routing | `weather/aviation/` topics include at least `metar`, `taf`, `qvaci` | Incomplete product list vs F6; not IWXXM XSD |
| [wmo-im/wis2-guide](https://github.com/wmo-im/wis2-guide) | informative | ops | States IWXXM (FM 205) for aeronautical MET on WIS2 / SWIM | Policy/ops prose |
| [wmo-im/GTStoWIS2](https://github.com/wmo-im/GTStoWIS2) | historical | `bulletin` | AHL → WIS2 topic mapping (GTS era) | **Archived**; points to `wis2-topic-hierarchy` + `wis2-notification-message` |
| [wmo-im/CCT](https://github.com/wmo-im/CCT) | normative-vocabulary (306 Vol **I.2**) | indirect | Common Code Tables working CSVs for Manual on Codes Part C | **Not** aviation TAC FM tables (4678 lives in Vol **I.1**); rarely primary for METAR groups |
| [wmo-im/saf](https://github.com/wmo-im/saf) | historical | lineage | Simple Aeronautical Features used in IWXXM 1.x | **Deprecated** / archived; replaced by AIXM profile |
| [wmo-im/metce](https://github.com/wmo-im/metce), [opm](https://github.com/wmo-im/opm), [met-basic](https://github.com/wmo-im/met-basic) | historical | lineage | Foundation packages referenced by older docs | Archived / deprecated; not Annex 3 TAC SoT |

### Tier C — not useful for Annex 3 TAC / IWXXM encode-validate

Vast majority of org (~90+ repos): GRIB2/BUFR4 pipelines, WCMP2/WMDR metadata, Hydro/WHOS, wis2box services, expert-team scratchpads, FOSS guides, etc.

Notable near-misses:

| Repo | Why skip for this scope |
|------|-------------------------|
| [pymetdecoder](https://github.com/wmo-im/pymetdecoder) | SYNOP/SHIP/MOBIL only — not aviation TAC |
| [VolumeC1](https://github.com/wmo-im/VolumeC1) | GTS CCCC list freeze notice; not product rules |
| [manuals](https://github.com/wmo-im/manuals) | Archived empty-ish “WMO Manuals” pointer; use WMO e-Library for 306 |
| BUFR4 / GRIB2 / CCT-translation | Table-driven / binary codes — wrong FM family for IWXXM TAC path |

**Annex 3 itself is not in this org** — ICAO Store paywall remains the SARP SoT for TAC templates / SPECI criteria / SIGMET wording.

---

## Product × artifact matrix (org-sourced)

| Product | TAC input artifact (org?) | IWXXM output (root / XSD) | Official example / guidance | Gap vs GIFTs | Consumer |
|---------|---------------------------|---------------------------|-----------------------------|--------------|----------|
| METAR / SPECI | examples + translation fixtures only (not Annex 3 text) | `metarSpeci.xsd` in `iwxxm` | `TAC-to-XML-Guidance` + examples | US REMARKS outside; nils | tac2iwxxm, iwxxm-validate |
| TAF | same | `taf.xsd` | examples CNL/NIL/AMD | Outside GIFTs depth | same |
| SIGMET / AIRMET | same | `sigmet.xsd` / `airmet.xsd` | examples + 49-2 phenomena lists | Entire product outside GIFTs | same |
| VAA / TCA | same | advisory XSDs | examples + colour / MetFeature | Outside GIFTs | same |
| Bulletin | AHL community page + COLLECT XSD (in `iwxxm`) | `collect` / `iwxxm-collect` | OPMET Guidelines (non-org) | Outside GIFTs | bulletin |
| WIS2 route | — | publish as IWXXM payload | wis2-cookbook / topic hierarchy | N/A to tac-validate | F8 / ops |

---

## Key findings

### 1. Concentration of value

Only **four** active repos form the IWXXM family; all are already named in `vendor/manifest.json` and `RULE_SOURCE_URLS.md`. The rest of `wmo-im` is mostly WIS2 / binary codes / hydrology / metadata.

### 2. Annex 3 vs IWXXM split

`wmo-im/iwxxm` **implements** Annex 3 / PANS-MET products in XML (README + topics `annex-iii`), but **does not publish** Annex 3 SARP text. TAC validation still needs ICAO Annex 3 + WMO 306 Vol I.1 (e-Library / store).

### 3. COLLECT

Stand-alone `wmo-im/collect` is a lineage reference (2017). Active bulletin validation should use collect schemas **vendored with** the iwxxm pin under `externalSchema/schemas.wmo.int/collect/`.

### 4. Codelists authority chain

`iwxxm-codelists` → `codes.wmo.int`. Discrepancy policy (README): **Manual on Codes** wins over CSV if they disagree.

### 5. Translation fixtures

`iwxxm-translation` explicitly disclaims official status — use for golden tests / coverage expansion, never as sole SoT over schema examples.

### 6. WIS2 aviation topics are thin

Topic hierarchy currently lists aviation `metar`, `taf`, `qvaci` under `weather/aviation/` — not a full F6 product map. Do not treat incomplete topic CSVs as product-scope SoT for converters.

---

## Catalog paste rows

```text
### wmo-im org (index) — IWXXM family vs rest
- Publisher: WMO Information Management
- URL: https://github.com/wmo-im
- Access: public
- Applies to: products=[F6+]; profiles=[annex3]; role=[conversion|iwxxm-validation|bulletin] (family only)
- Gap vs GIFTs: multi-product schemas + advisories outside GIFTs
- Consumer: tac2iwxxm | iwxxm-validate | bulletin (Tier A); F8 topic routing (Tier B)
- Label: informative index (point into Tier A repos)
- Caveats: Annex 3 PDF not hosted here; ignore BUFR/GRIB/Hydro/WMDR majority
- Mined: 2026-07-14

### wmo-im/collect (lineage only)
- Publisher: WMO
- URL: https://github.com/wmo-im/collect
- Access: public
- Applies to: products=[bulletin]; role=[bulletin]
- Consumer: bulletin (historical compare only)
- Label: historical
- Caveats: superseded for runtime by collect XSD inside wmo-im/iwxxm externalSchema at active pin
- Mined: 2026-07-14

### wmo-im/wis2-cookbook (aviation publish)
- Publisher: WMO
- URL: https://github.com/wmo-im/wis2-cookbook/blob/main/cookbook/sections/data-publishers/publishing-aviation-data.adoc
- Access: public
- Applies to: products=[aviation IWXXM on WIS2]; role=[bulletin]
- Consumer: F8 / ops
- Label: informative
- Caveats: use-rights / publish practices — not TAC grammar
- Mined: 2026-07-14
```

---

## Domain-knowledge cross-check (required on full / refresh passes)

| Older claim (doc + date/edition) | This source finding | Action |
|----------------------------------|---------------------|--------|
| Stand-alone COLLECT may appear equal to iwxxm examples for bulletin (historical docs) | Active pin ships collect under `iwxxm` `externalSchema`; standalone repo stale since 2017 | Caveat stand-alone `collect` as historical; prefer pin path |
| Incomplete assumption that “all WMO codes useful for METAR are in CCT” | CCT = Vol I.2 common tables; aviation weather TAC still 306/4678 + 49-2 | Keep CCT demoted; do not promote to primary Annex 3 row |
| WIS2 topic hierarchy as F6 product inventory | Only metar/taf/qvaci seen under aviation | Keep partial; do not expand COVERAGE_MATRIX products from topics alone |

---

## Implications for this repo

- **F6 / tac2iwxxm:** Keep mining `iwxxm` examples + guidance + 49-2 registers; optionally expand fixtures from `iwxxm-translation` labeled informative.
- **tac-validate:** Do **not** expect new Annex 3 grammar from this org; stay on ICAO store + WMO 306 I.1 landings already in catalog.
- **iwxxm-validate:** Vendor pin remains SoT; modelling repo for understanding SCH provenance only.
- **Caveats / TBD:** Optional deeper pass on `iwxxm/documentation/manual/FM205.adoc` vs printed WMO-306 Vol I.3 (edition drift vs v2025-2).

---

## Suggested next mining passes

1. Diff `documentation/manual/FM205.adoc` @ `v2025-2` against WMO-306 Vol I.3 mining notes for superseded package tables.
2. Inventory `iwxxm-translation` products × Amendment folders vs F6 matrix (informative only).
3. Map WIS2 aviation topic gaps (SPECI, SIGMET, AIRMET, VAA, TCA, SWX) if F8 needs routing labels.
```
