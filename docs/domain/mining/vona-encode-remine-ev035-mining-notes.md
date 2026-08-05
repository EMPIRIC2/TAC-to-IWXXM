# Mining notes — VONA encode remine (EV-035 / S043)

> **Transitory** — promote durable rows to RULE_SOURCE_URLS / COVERAGE_MATRIX / PROVENANCE_MAP.  
> **Cycle**: S043 / EV-035 · **Date mined**: 2026-08-05  
> **Skill**: mine-domain-sources (remine Gap 1)  
> **Prior**: S040 cookbook `t2.1-vona-encode-cookbook.md`

## Scope

Confirm whether any **new** public/vendor source supplies TAC→IWXXM VONA token mapping
beyond XSD / SCH / `vona-A7-1` / PANS-MET cite.

## Findings

| Source | Access | VONA encode content? |
|--------|--------|----------------------|
| `2025-2/IWXXM/examples/TAC-to-XML-Guidance.txt` | public / vendor | **No** — confirmed 2026-08-05 |
| `documentation/webpages/AHL.asciidoc` | vendor tree | **Yes** — TAC `W`/`M` → VONA; IWXXM `L`/`M` → `VolcanoObservatoryNoticeForAviation` |
| `documentation/manual/FM205.adoc` | vendor tree | **Yes** — VONA package **1.0.0**; `https://schemas.wmo.int/iwxxm/2025-2/vona.xsd` |
| `ReleaseNotes-IWXXM.txt` | vendor | Package RC notes + example revise |
| `vona.xsd` + `rule/iwxxm.sch` + `vona-A7-1` | vendor pin | Unchanged SoT for element/business rules |
| ICAO PANS-MET Doc 10157 | paywall | Cite-only (unchanged) |

## Conflict / defer

Guidance remains **silent** for VONA tokens. Do **not** invent Guidance rows. Encode SoT =
AHL T1T2 + FM205 package line + XSD/SCH + official peer + cookbook (S040).

## Promote targets

- RULE_SOURCE_URLS: AHL.asciidoc + FM205.adoc rows (if not already) with `products=[VONA]`
- COVERAGE_MATRIX VONA conversion: ⚠ Guidance silent **and** ✅ AHL/FM205/XSD/peer
- PROVENANCE_MAP: rule ids for VONA encode fields

## Ticket

Residual: no TAC-to-XML-Guidance VONA section → GitHub issue under #846 (see
`provenance-gaps.md`).
