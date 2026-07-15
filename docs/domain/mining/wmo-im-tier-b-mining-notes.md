# wmo-im Tier B local clones — mining notes

**Status:** working notes (not normative). Verify against official registry / schemas.  
**Focus of this pass:** pull Tier B repos locally; mine exchange / lineage / parallel vocab for Annex 3 · IWXXM · F8  
**Ticket:** pairs with [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Local clones (gitignored):** `.local/reference/wmo-im-tier-b/`

**Promote durable findings into:**

| Doc | Path |
|-----|------|
| Domain hub | [../README.md](../README.md) |
| TAC validation | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Org survey | [wmo-im-org-mining-notes.md](./wmo-im-org-mining-notes.md) |
| Tier A deep mine | [wmo-im-tier-a-mining-notes.md](./wmo-im-tier-a-mining-notes.md) |

| Item | Value |
|------|-------|
| Title | Tier B local mine (collect, WIS2*, GTStoWIS2, CCT, saf/metce/opm/met-basic) |
| Publisher | WMO Information Management (`wmo-im`) |
| Official landings | https://github.com/wmo-im/{collect,wis2-cookbook,wis2-topic-hierarchy,wis2-guide,GTStoWIS2,CCT,saf,metce,opm,met-basic} |
| Pin / edition | Runtime collect/metce/opm/saf via `vendor/schemas/iwxxm/externalSchema/`; WIS2 topics tip 2026-07-13 |
| Date mined | 2026-07-14 |
| Access | public |
| Label | mixed: historical / informative / normative-exchange (WIS2) / normative-vocabulary (CCT I.2) |

---

## Local checkout inventory

| Dir under `.local/reference/wmo-im-tier-b/` | Branch @ short SHA | Last commit | Notes |
|--------------------------------------------|--------------------|-------------|-------|
| `collect/` | `master` @ `14ad69f` | 2017-07-27 | XSD **1.1** + **1.2**; byte-identical to vendor `externalSchema/.../collect/1.2/collect.xsd` |
| `wis2-cookbook/` | `main` @ `5db0067` | 2026-06-11 | Aviation publish recipe |
| `wis2-topic-hierarchy/` | `main` @ `81134f0` | 2026-07-13 | Current WTH CSVs |
| `wis2-guide/` | `main` @ `a48341f` | 2026-06-17 | WIS2↔SWIM §2.8.1.1 |
| `GTStoWIS2/` | `main` @ `a29ec78` | 2023-03-13 | Archived AHL→topic; not current WTH |
| `CCT/` | `master` @ `8d5866c` | 2026-04-27 | Common Code Tables C00–C14 |
| `saf/` | `master` @ `5ad0839` | 2017-09-27 | Deprecated; IWXXM 1.x only |
| `metce/` | `master` @ `3ecd2eb` | 2017-10-24 | Through **1.2**; also vendored under iwxxm externalSchema |
| `opm/` | `master` @ `0230b10` | 2017-10-24 | Through **1.2** |
| `met-basic/` | `master` @ `7821d43` | 2017-10-24 | **1.0RC1** only; aeronautical quantity types |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Bulletin COLLECT schema lineage + confirmation it matches the active iwxxm pin | TAC FM templates / Annex 3 SARP text |
| Current WIS2 publish guidance (Annex 3 **use-rights**, recommended policy, thin aviation topics) | Encode/validate SoT for METAR…TCA XML |
| Historical GTS AHL → topic dictionary (richer T1T2 than current WTH aviation folder) | Live F8 routing table (prefer `wis2-topic-hierarchy`) |
| CCT Part C (Vol I.2) centres/units for TDCF | Code table **4678** / 49-2 aviation weather lists |

---

## Product × artifact matrix

| Product | Input (TAC / AHL / …) | Output (IWXXM / WIS2) | Official example or register | Gap vs GIFTs | Consumer |
|---------|----------------------|------------------------|------------------------------|--------------|----------|
| METAR | TAC AHL `SA`; IWXXM AHL `LA` | COLLECT wrap; WIS2 topic `…/weather/aviation/metar` (current) | Cookbook + WTH CSV | Outside GIFTs bulletin path | bulletin, F8 |
| SPECI | TAC `SP`; IWXXM `LP` | **No** SPECI leaf in current WTH aviation CSV; GTStoWIS2 mapped `SP` → `…/aviation/speci` | Historical TableA | Topic gap vs F6 | F8 watch |
| TAF | TAC `FC`/`FT`; IWXXM `LC`/`LT` | WTH `taf`; GTStoWIS2 `L C/T` → aviation-XML/taf | Cookbook + Guide | — | F8 |
| SIGMET / AIRMET / VAA / TCA | TAC `WS`/`WA`/`WV`/`WC`/`FK`/`FV` | **Absent** from current `weather/aviation/index.csv`; GTStoWIS2 had `W*` and `L*` aviation-XML paths | Historical only | Entire products | F8 TBD |
| QVACI | IWXXM-native | WTH `qvaci` + Guide example topic | Guide §2.8.1.1.3 | Outside F6 core | F8 / ops |
| Bulletin | COLLECT `MeteorologicalBulletin` | Still used in IWXXM/AMHS; WIS2 Guide: **does not** group into bulletins | collect 1.2 + OPMET Guidelines | Outside GIFTs | bulletin vs F8 model diverge |

---

## Key findings

### 1. `collect` — confirm vendor, then ignore stand-alone for runtime

- Namespace: `http://def.wmo.int/collect/2014`, root `MeteorologicalBulletin`.
- `collect/1.2/collect.xsd` SHA-256 equals vendor pin copy under `vendor/schemas/iwxxm/externalSchema/schemas.wmo.int/collect/1.2/`.
- Stand-alone repo still useful as **lineage / ReleaseNotes** (1.1 Jun 2015 → 1.2 Aug 2016); last git activity 2017.
- **Action:** validate bulletins against **vendored** collect + `iwxxm-collect.xsd`, not a fresh clone of `wmo-im/collect`.

### 2. WIS2 topic hierarchy — aviation leaf is thin

File: `topic-hierarchy/earth-system-discipline/weather/aviation/index.csv`:

| Name | Description | Status |
|------|-------------|--------|
| `metar` | Aerodrome observation | Operational |
| `taf` | Aerodrome forecast | Operational |
| `qvaci` | Quantitative volcanic ash concentration information | Operational |

No SPECI, SIGMET, AIRMET, VAA, TCA, SWX, VONA under this folder (as of `81134f0`). Registry landing cited by cookbook: `http://codes.wmo.int/wis/topic-hierarchy/earth-system-discipline/weather/aviation`.

Do **not** expand F6 coverage from WTH alone.

### 3. `wis2-cookbook` — Annex 3 use-rights, not TAC rules

`cookbook/sections/data-publishers/publishing-aviation-data.adoc`:

- Aeronautical MET may only be used for international air navigation (Annex 3 cite).
- Publish as **recommended** data policy; require `rights` + license link in WCMP2 metadata.
- Example topic: `origin/a/wis2/{centre-id}/data/recommended/weather/aviation/metar`.
- Embed warning: embedding IWXXM in WNMs makes payload openly visible on WIS2.

### 4. `wis2-guide` — IWXXM for SWIM + COLLECT ID vs non-bulletin WIS2

`guide/sections/part2/operations.adoc` §2.8.1.1:

- Format for SWIM: **IWXXM (FM 205)**; Annex 3 for content specs.
- ICAO AFS exchange **out of scope** of the Guide.
- WIS2 publishes **individual** resources + notifications — **does not group into bulletins** (explicit contrast to GTS).
- Unique ID footnote: GTS AHL in **COLLECT envelope** (`TTAAii CCCC YYGGgg`) usable when TAC↔IWXXM exists; `gml:identifier` for newer IWXXM-only products (WAFS, QVACI); **no agreed** unique ID for individual METAR/TAF aerodrome reports.
- Retain ≥24 h at node for SWIM gateway.

### 5. `GTStoWIS2` — historical AHL product map (richer than current WTH)

Archived; README points to `wis2-topic-hierarchy` + `wis2-notification-message`.

`TableA.json` still encodes GTS T1T2 → topic paths useful as **lineage** when reconciling AHL with F6:

| TT (examples) | Historical topic fragment |
|---------------|---------------------------|
| `SA` | `…/aviation/metar` |
| `SP` | `…/aviation/speci` |
| `FC`/`FT` | `…/aviation/taf` |
| `WA` | `…/aviation/airmet` |
| `WS` | `…/aviation/sigmet` |
| `WC` / `WV` | cyclone / ash SIGMET |
| `LA`/`LP`/`LC`/`LT`/`LS`/`LW`/`LU`/`LV`/`LY`/`LK`/`LN` | `aviation-XML/…` (IWXXM T1=`L`) |

Caveat: `mapAHLtoExtension` returns `.iwxxm` only for TT `LT`; other `L*` mostly get non-iwxxm extensions — **do not** trust extension heuristic for modern AMHS `A_…xml.gz` naming (prefer OPMET Guidelines + AHL community page).

### 6. `CCT` — Vol I.2 only

Tables C00–C14 / COV: GRIB/BUFR/CREX master versions, originating centres, radiosondes, units, etc. Includes e.g. NCEP **Aviation Weather Center** as a C12 sub-centre — operational metadata, **not** TAC weather group vocabulary. Keep demoted vs 306/4678 and `iwxxm-codelists` **49-2**.

### 7. Foundation packages (`saf` / `metce` / `opm` / `met-basic`)

| Repo | Role for us |
|------|-------------|
| `saf` | Deprecated; README → AIXM WX profile. Still mirrored under vendor `externalSchema/.../saf/` for older docs / examples lineage |
| `metce` 1.2 | `TropicalCyclone`, `Volcano`, `EruptingVolcano` feature types — still relevant as types referenced from IWXXM advisories; prefer vendor embed |
| `opm` 1.2 | Observable property scaffolding |
| `met-basic` 1.0RC1 | One-shot aeronautical quantity palette (`cloudAeronautical.xsd`, `aeronauticalMeteorology.xsd`, …) — no further development |

---

## Catalog paste rows

```text
### wmo-im Tier B local dig (2026-07-14)
- Local: .local/reference/wmo-im-tier-b/
- Notes: docs/domain/mining/wmo-im-tier-b-mining-notes.md
- collect 1.2 == vendor externalSchema (runtime: vendor)
- WTH aviation leaves: metar, taf, qvaci only
- WIS2 Guide: no bulletin grouping; IWXXM for SWIM; COLLECT AHL as ID when TAC pair exists
- GTStoWIS2: historical AHL→topic (archived)
- CCT: Vol I.2 only — not 4678
```

---

## Domain-knowledge cross-check

| Older claim (doc + date/edition) | This source finding | Action |
|----------------------------------|---------------------|--------|
| Org survey: standalone collect “stale / prefer iwxxm externalSchema” | SHA match proves pin **is** collect 1.2; stand-alone = same bytes + ReleaseNotes | Keep prefer-vendor; add “content-identical to stand-alone 1.2” |
| Org survey: WTH has “at least metar/taf/qvaci” | Confirmed **only** those three Operational leaves | Strengthen caveat: SPECI+hazard products **missing** from WTH aviation CSV |
| Imply WIS2 bulletin == IWXXM COLLECT | Guide: WIS2 does **not** group into bulletins | Split roles: COLLECT for AMHS/IWXXM bulletin; WIS2 = one resource per notification |
| GTStoWIS2 as current topic SoT | Archived; supersede with WTH + codes.wmo.int wis topic hierarchy | Label GTStoWIS2 **historical**; keep TableA as AHL lineage aid only |
| CCT useful for METAR weather tokens | Confirmed Part C common / centres / units | No promotion into TAC_VALIDATION weather SoT |

---

## Implications for this repo

- **F6 / tac2iwxxm:** No new TAC→XML field rules. COLLECT wrapping still from pin examples + OPMET Guidelines. metce TropicalCyclone/Volcano types already via vendor externalSchema.
- **tac-validate:** Nothing new from Tier B for Annex 3 templates.
- **iwxxm-validate:** Confirm collect/metce/opm/saf resolution via vendor `externalSchema`; no need to vendor stand-alone repos.
- **F8 / bulletin:** Prefer WTH + cookbook/guide for WIS2 routing/metadata; track missing WTH leaves as product-topic TBD; do not assume COLLECT packing on WIS2.
- **Caveats / TBD:** Watch WTH aviation CSV for SPECI/SIGMET/AIRMET/VAA/TCA leaves; keep GTStoWIS2 TableA only as migration lineage.

---

## Suggested next mining passes

1. ~~Diff vendor `externalSchema` metce vs tip~~ — **done** 2026-07-14: published [schemas.wmo.int/metce/1.2](https://schemas.wmo.int/metce/1.2/) ≡ vendor after C14N ([schemas-wmo-int-metce-mining-notes.md](./schemas-wmo-int-metce-mining-notes.md)). ~~Same for opm~~ — **done** 2026-07-14 ([schemas-wmo-int-opm-mining-notes.md](./schemas-wmo-int-opm-mining-notes.md)). Saf still open.
2. If F8 needs full F6 routing, raise product-topic mapping decision (WTH gap vs GTS AHL table).
3. Cross-link Guide “no bulletin” vs OPMET Guidelines COLLECT for dual-path ops docs.
