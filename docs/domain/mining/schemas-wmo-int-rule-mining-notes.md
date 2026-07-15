# schemas.wmo.int/rule — focused mining notes

**Status:** working notes (not normative). Verify against official registry / schemas.  
**Focus of this pass:** Centralized Schematron drop at `schemas.wmo.int/rule/` · relationship to pin-path `…/iwxxm/<ver>/rule/` and foundation `…/{metce,opm,collect}/<ver>/rule/` · role `iwxxm-validation` (lineage)  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Local extracts (if any, gitignored):** none (used published HTTP + vendor package-local embeds)

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
| Title | WMO centralized Schematron index (`schemas.wmo.int/rule/`) |
| Publisher | World Meteorological Organization (schemas.wmo.int) |
| Official landing | https://schemas.wmo.int/rule/ |
| Pin / edition | Packages **1.0**, **1.1**, **1.2** (index last-modified **2019-10-11**); **not** the runtime path for IWXXM **v2025-2** |
| Date mined | 2026-07-14 |
| Access | public |
| Label | historical (IWXXM 1.x SCH under 1.0/1.1) · normative-schema mirror only for `/rule/1.2/{metce,opm,collect}.sch` (= package-local) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Top-level WMO schema-repo folder that hosted **shared Schematron** for early IWXXM / SAF / METCE / OPM / COLLECT package lines | The runtime Schematron path for IWXXM **2025-2** (or any year-versioned IWXXM line) |
| Directory listing: [1.0](https://schemas.wmo.int/rule/1.0/) · [1.1](https://schemas.wmo.int/rule/1.1/) · [1.2](https://schemas.wmo.int/rule/1.2/) | A vocabulary register or Annex 3 TAC SoT |
| Byte-identical **mirror** (2026-07-14) of foundation SCH already published under `metce/1.2/rule/`, `opm/1.2/rule/`, `collect/1.2/rule/` | A place that still publishes current `iwxxm.sch` after 1.1 |
| Sibling of `metce/` · `opm/` · `collect/` · `saf/` on [schemas.wmo.int](https://schemas.wmo.int/) | Vendored as `externalSchema/.../rule/` — vendor has **no** top-level `schemas.wmo.int/rule/` tree |

---

## Product × artifact matrix

| Product | Input (TAC / …) | Output (IWXXM / …) | Official example or register | Gap vs GIFTs | Consumer |
|---------|-----------------|--------------------|------------------------------|--------------|----------|
| METAR / SPECI / TAF | — | **Historical only:** `/rule/1.0\|1.1/iwxxm.sch` → ns `http://icao.int/iwxxm/1.0\|1.1` (63 patterns) | Prefer [iwxxm/2025-2/rule/iwxxm.sch](https://schemas.wmo.int/iwxxm/2025-2/rule/iwxxm.sch) (165 patterns, ns `…/2025-2`) | N/A for modern pin | `iwxxm-validate` (do **not** use `/rule/` for pin) |
| SIGMET (VA / TC members) | — | Patterns `VolcanicAshSIGMET*` / `TropicalCycloneSIGMET*` in 1.x SCH only | Same — use pin SCH | Outside GIFTs | same |
| AIRMET / VAA / TCA / VONA / SWX / WAFS | — | **Absent** from `/rule/*/iwxxm.sch` | Covered only in year-versioned `iwxxm/<ver>/rule/iwxxm.sch` | Outside GIFTs | same |
| Bulletin (COLLECT) | multi-report wrap | `/rule/1.1\|1.2/collect.sch` — **1.2 identical** to `collect/1.2/rule/collect.sch` | Prefer package URL or vendor embed | Outside GIFTs | `iwxxm-validate` / bulletin |
| METCE / OPM scaffolding | — | `/rule/1.2/{metce,opm}.sch` **identical** to package-local | Prefer `metce/1.2/rule/`, `opm/1.2/rule/` cites | N/A | `iwxxm-validate` (ancillary) |
| SAF (aerodrome features) | — | `/rule/1.0\|1.1/saf.sch` (ns `icao.int/saf/1.0\|1.1`) | SAF deprecated → AIXM; see vendor `saf/{1.0,1.1}/rule/` | Historical | lineage only |

---

## Key findings

### Published tree (2026-07-14)

Landing [https://schemas.wmo.int/rule/](https://schemas.wmo.int/rule/) lists only **1.0**, **1.1**, **1.2**.

| Package | Files | Notes |
|---------|-------|-------|
| **1.0** | `iwxxm.sch`, `metce.sch`, `opm.sch`, `saf.sch` | IWXXM ns **1.0**; no `collect.sch` |
| **1.1** | above + `collect.sch` | IWXXM / SAF ns **1.1**; IWXXM SCH ≈ 1.0 body with ns bump only |
| **1.2** | `collect.sch`, `metce.sch`, `opm.sch` only | **Dropped** `iwxxm.sch` and `saf.sch` — aligns with foundation package **1.2** era |

All index listings share last-modified **2019-10-11** (snapshot date on the mirror, not necessarily authorship date of each SCH).

### Do not confuse path shapes

| Path shape | Meaning for this repo |
|------------|------------------------|
| `https://schemas.wmo.int/rule/<1.0\|1.1\|1.2>/*.sch` | Centralized / early-line Schematron index (this dig) |
| `https://schemas.wmo.int/iwxxm/<YYYY-N>/rule/iwxxm.sch` | **Runtime** product Schematron for that IWXXM line |
| `https://schemas.wmo.int/{metce,opm,collect,saf}/<ver>/rule/*.sch` | Package-local SCH (preferred cite for foundations) |
| `vendor/.../IWXXM/rule/iwxxm.sch` + `externalSchema/.../{metce,opm,collect}/…/rule/` | CI / offline truth under pin **v2025-2** |

There is **no** `https://schemas.wmo.int/rule/iwxxm.sch` at the landing root.

### Historical IWXXM Schematron (`/rule/1.0` · `/rule/1.1`)

- Query binding: Schematron `xslt2`.
- Namespaces: `http://icao.int/iwxxm/1.0` vs `…/1.1` (and matching SAF).
- **63** patterns; ID style `METAR1` … `TAF11` … `TropicalCycloneSIGMET8` (no dotted `PRODUCT.RuleId` naming used in 2025-2).
- Product coverage: METAR, SPECI, TAF, VA SIGMET, TC SIGMET (+ runway-state / sea-state / present-weather record rules). **No** AIRMET, advisory (VAA/TCA), VONA, SWX, WAFS patterns.
- Includes **`AerodromeRunwayState*`** patterns — runway state **removed** from IWXXM **2025-2** RC1 (already flagged in catalog for the pin).
- **1.0 vs 1.1 `iwxxm.sch`:** namespace URIs differ; pattern bodies otherwise match (trailing newline only beyond ns).

Contrast pin Schematron: [2025-2 `iwxxm.sch`](https://schemas.wmo.int/iwxxm/2025-2/rule/iwxxm.sch) — ns `http://icao.int/iwxxm/2025-2`, **165** patterns, RDF `document()` codelist checks, dotted pattern IDs.

### Foundation SCH under `/rule/1.2/` (= package-local)

Verified **byte-identical** (2026-07-14) to:

| Centralized | Package-local / vendor |
|-------------|------------------------|
| `/rule/1.2/metce.sch` | `metce/1.2/rule/metce.sch` = vendor `externalSchema/.../metce/1.2/rule/metce.sch` |
| `/rule/1.2/opm.sch` | `opm/1.2/rule/opm.sch` = vendor embed |
| `/rule/1.2/collect.sch` | `collect/1.2/rule/collect.sch` = vendor embed |

IDs match prior METCE/OPM digs (`METCE.MC*`, `METCE.RB1`, `OPM.*`, `COLLECT.MB1`). Published `OPM.COP1` still uses malformed assert XPath `{if(...)}` (same caveat as OPM mining notes).

**1.1 → 1.2** foundation files are **not** identical: 1.2 renames pattern IDs to dotted `PACKAGE.RULE` form and refreshes assert text / XML decl.

### Vendor embed

- Pin tree vendors package-local `…/rule/*.sch` under `metce` / `opm` / `collect` / `saf` — **not** a copy of `schemas.wmo.int/rule/`.
- No `schemaLocation` / citation under pin XSD pointing at `schemas.wmo.int/rule/` found in this pass.
- GitHub development remains [wmo-im](https://github.com/wmo-im); this landing is the published HTTP mirror family.

---

## Catalog paste rows

```text
### WMO schemas.wmo.int/rule (centralized Schematron index)
- Publisher: WMO
- URL: https://schemas.wmo.int/rule/
- Stable concept pattern: /rule/{1.0|1.1|1.2}/*.sch (not year-versioned IWXXM)
- Access: public
- Applies to: products=[METAR,SPECI,TAF,SIGMET] (1.x SCH only); foundations METCE/OPM/COLLECT via 1.2 mirror; profiles=[annex3]; role=[iwxxm-validation]
- Gap vs GIFTs: historical IWXXM 1.x pattern set; missing AIRMET/VAA/TCA vs current pin
- Consumer: iwxxm-validate (lineage / discovery only — prefer pin + package-local SCH)
- Label: historical (iwxxm/saf under 1.0–1.1); normative-schema mirror for rule/1.2/{metce,opm,collect}.sch only
- Caveats: Do not validate 2025-2 XML against /rule/1.0|1.1/iwxxm.sch. Runtime SoT = schemas.wmo.int/iwxxm/<pin>/rule/iwxxm.sch + vendor. /rule/1.2 foundation SCH == package-local; prefer package URLs in citations.
```

---

## Domain-knowledge cross-check (required on full / refresh passes)

| Older claim (doc + date/edition) | This source finding | Action (supersede / caveat / keep as historical) |
|----------------------------------|---------------------|--------------------------------------------------|
| Canonical Schematron cite = `schemas.wmo.int/iwxxm/2025-2/rule/iwxxm.sch` | Confirmed: centralized `/rule/` does **not** host 2025-2 `iwxxm.sch` | **Keep** pin path as SoT; caveat `/rule/` as historical aggregate |
| METCE/OPM digs: SCH lives under `metce/1.2/rule/`, `opm/1.2/rule/` | `/rule/1.2/{metce,opm}.sch` byte-identical | **Keep** package-local preferred cite; note alternate mirror URL |
| Doc 10003 / early IWXXM docs may imply a single “rule” package | `/rule/1.0|1.1` = IWXXM **1.x** only (63 patterns; runway state present) | Mark **historical**; never mix with 2025-2 XML |
| Org survey: foundation SCH via package trees | Centralized `/rule/` is a sibling index on schemas.wmo.int, frozen ~2019 listing | Document as discovery/lineage; no new consumer wiring |

---

## Implications for this repo

- **F6 / tac2iwxxm:** No encode mapping from this tree; ignore for TAC→XML.
- **tac-validate:** Out of scope (not TAC SARPs).
- **iwxxm-validate:** Continue pin `vendor/schemas/iwxxm/…/IWXXM/rule/iwxxm.sch` (+ RDF) and foundation embeds under `externalSchema/.../{metce,opm,collect}/…/rule/`. Do **not** add `schemas.wmo.int/rule/` as a validate root.
- **Caveats / TBD:** ~~Optional next pass on schemas.wmo.int/saf/~~ — **done** 2026-07-14: [schemas-wmo-int-saf-mining-notes.md](./schemas-wmo-int-saf-mining-notes.md).

---

## Suggested next mining passes

1. ~~[schemas.wmo.int/saf/](https://schemas.wmo.int/saf/) — deprecated SAF vs AIXM~~ — **done** 2026-07-14: [schemas-wmo-int-saf-mining-notes.md](./schemas-wmo-int-saf-mining-notes.md).
2. [schemas.wmo.int/collect/](https://schemas.wmo.int/collect/) full package landing (XSD + SCH) if bulletin dig needs HTTP package tree (vendor already has 1.2).
3. Confirm whether any older GitHub wiki / Doc 10003 drafts deep-link `/rule/1.0/iwxxm.sch` for citation hygiene in mining notes already touching IWXXM 1.x.
