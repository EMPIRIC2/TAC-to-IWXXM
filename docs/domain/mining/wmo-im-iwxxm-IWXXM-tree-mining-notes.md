# Mining notes — wmo-im/iwxxm `IWXXM/` tree (#804)

> **Transitory** — not SoT. Promote durable rows to RULE_SOURCE_URLS / COVERAGE_MATRIX / canonicals.  
> **Cycle**: S031 / EV-024 · **Date mined**: 2026-07-30  
> **Skill**: mine-domain-sources  
> **Runtime SoT**: `vendor/manifest.json` → IWXXM **v2025-2**  
> SHA `35180cbe3bec0bc536a78714dd78d2e7ba60931f` · path `vendor/schemas/iwxxm/2025-2/IWXXM/`

## Source classification

| Field | Value |
|-------|-------|
| Source | https://github.com/wmo-im/iwxxm → `IWXXM/` |
| Published | https://schemas.wmo.int/iwxxm/2025-2/ |
| Label | normative-schema + normative-examples + Schematron |
| Access | public (GitHub + schemas.wmo.int) |
| Products | METAR/SPECI/TAF/SIGMET/AIRMET/VAA/TCA (+ SWX/VONA/WAFS/QVACI roadmap) |
| Roles | conversion · iwxxm-validation · UI catalog |
| Ticket | #804 |

## Folder × relevancy (pin tree)

Walked against **vendor pin** (not bare `master` tip). Sibling dirs (`documentation/`,
`externalSchema/`, `bin/`) are **not** in the pin snapshot — triage via #807 / optional
`.local/` clone; do not invent pin content.

### A. `IWXXM/` package proper

| Path | Contents summary | Normative? | In vendor pin? | Used today? | Action |
|------|------------------|------------|----------------|-------------|--------|
| `IWXXM/examples/` | Official TAC↔XML pairs, NIL/COLLECT, translation-failed, IWXXM-only WAFS/QVACI, Guidance.txt | Yes (examples + guidance notes) | Yes (~55 files / 30 stems) | Partial catalog + goldens | **Wire** in-scope; matrix below |
| `IWXXM/rule/iwxxm.sch` | Package Schematron | Yes | Yes | `iwxxm-validate` | Confirm parity; re-scrape assert ids (M4) |
| `IWXXM/rule/*.rdf` | Offline 49-2 / iwxxm / common-nil / bufr4 vocab | Yes (vocab for SCH) | Yes | Dual-register / nil (EV-023) | Keep; cite in matrix |
| `IWXXM/*.xsd` (product + common) | metarSpeci, taf, sigmet, airmet, VAA, TCA, SWX, VONA, WAFS, QVACI, collect, common, gml, metFeature, iwxxm | Yes | Yes | Convert/validate for in-scope | P0 in-scope; **defer** WAFS/QVACI encode |
| `IWXXM/ReleaseNotes-IWXXM.txt` | Package changelog | Informative | Yes | Docs/drift | Cite on sync |
| `IWXXM/html/` | Packaged HTML zip/docs | Informative | Yes (dir) | No | Ignore for encode |
| `IWXXM/XMI/` | UML XMI | Informative | **Absent on pin** | No | Defer; pair with modelling (#807) |

### B. Repo siblings (not in pin — #807 / tip triage)

| Path | Role | Relevancy | Action |
|------|------|-----------|--------|
| `documentation/manual/FM205.adoc` | FM 205 AsciiDoc | High (encode/validate prose) | #807 / optional `.local/` |
| `documentation/guidanceDocs/` etc. | Guidance / regs | Triage | Promote only durable |
| `externalSchema/` | AIXM/ISO/METCE embeds | Validate resolve | Prefer schemas.wmo.int + vendor |
| `bin/` | Upstream validate helpers | Informative | Compare to our gates |
| `catalog.template.xml`, `LATEST_VERSION` | Packaging | Low | Sync tooling only |

## Stem × surface matrix

**Legend**: V = validate/CI · C = convert golden (canonicalize) · U = UI sample menu · D = defer  
**Tiers**: `pass` = wmoPass · `ref` = wmoReference · `—` = not in happy-path menu

| Stem | Product | V | C | U | Tier / note |
|------|---------|---|---|---|-------------|
| metar-A3-1 | METAR | ✅ | ✅ | ✅ | pass (catalog) |
| speci-A3-2 | SPECI | ✅ | ✅ | ✅ | pass |
| taf-A5-1 | TAF | ✅ | ✅ | ✅ | pass |
| taf-A5-2 | TAF | ✅ | ✅ | ✅ | pass |
| sigmet-A6-1a-TS | SIGMET | ✅ | ✅ | ✅ | pass |
| sigmet-A6-1b-CNL | SIGMET | ✅ | ✅ | ✅ | pass |
| sigmet-A6-2-TC | TC SIGMET | ⚠ | D | D | #738 quality; validate OK; menu defer until product bar |
| sigmet-VA-EGGX | VA SIGMET | ✅ | ⚠ | **ref** | Package golden exists; menu as reference if not already listed |
| sigmet-multi-location-VA | VA SIGMET | ⚠ | D | **ref** | Wire validate; menu reference (M5) |
| airmet-A6-1a-TS | AIRMET | ✅ | ✅ | ✅ | pass |
| airmet CNL peer | AIRMET | — | — | D | Not in vendor examples set as separate stem |
| va-advisory-A7-2 | VAA | ✅ | ✅ | ✅ | pass |
| tc-advisory-A2-2 | TCA | ✅ | ✅ | ✅ | pass |
| metar-NIL-collect | METAR/COLLECT | ✅ | D | — | Validate shape; not happy-path sample |
| taf-NIL-collect | TAF/COLLECT | ✅ | D | — | Validate shape |
| metar-translation-failed | METAR | ✅ | — | — | Quarantine matrix (#800); **not** sample menu |
| taf-translation-failed | TAF | ✅ | — | — | Quarantine |
| airmet-translation-failed | AIRMET | ✅ | — | — | Quarantine |
| sigmet-translation-failed-collect | SIGMET | ✅ | — | — | Quarantine |
| va-advisory-translation-failed | VAA | ✅ | — | — | Quarantine |
| tc-advisory-translation-failed | TCA | ✅ | — | — | Quarantine |
| spacewx-A7-3/4/5 (+ alt) | SWX | D | D | D | #740; S02.M2 |
| spacewx-translation-failed | SWX | D | — | — | Quarantine / roadmap |
| vona-A7-1 | VONA | D | D | D | #741; S02.M2 |
| WAFS-Example | WAFS | D | D | D | IWXXM-only; S02.M2 |
| qvaci-Example | QVACI | D | D | D | IWXXM-only; S02.M2 |
| TAC-to-XML-Guidance.txt | — | — | — | — | Re-scrape M4 → promote / children |

### M5 sample-menu wiring priority (product-in-scope + TAC, not yet / partial)

| Stem | Proposed U tier | Rationale |
|------|-----------------|-----------|
| sigmet-VA-EGGX | ref (or pass if equal) | Official VA SIGMET; operator value |
| sigmet-multi-location-VA | ref | Official multi-location VA |
| *(second METAR/SPECI/AIRMET/VAA/TCA)* | — | No second official stem in vendor set for METAR/SPECI/AIRMET/VAA/TCA — FIXTURE_GAPS stays unless tip adds stems |

Note: Vendor set has **one** METAR/SPECI/AIRMET/VAA/TCA happy-path stem each. “Second example”
gaps are not closable from this pin without inventing TAC — keep FIXTURE_GAPS rows; do not invent.

## Findings → consumers

| Finding | Consumer | Durable? |
|---------|----------|----------|
| Official examples under pin | UI catalog + validate CI | Yes — wire UJ-039 |
| `rule/iwxxm.sch` + RDF | iwxxm-validate | Already pinned |
| Guidance.txt nil/omit rules | tac2iwxxm / children | Partial (EV-023); re-scrape M4 |
| WAFS/QVACI XSD + examples | Roadmap | Defer features |
| Sibling documentation/ | #807 | Org pass |

## Child-issue seeds (encode/lint — not this dig)

| Gap | Suggested child / existing |
|-----|----------------------------|
| TC SIGMET A6-2 encode bar | #738 |
| SWX / VONA quality | #740 / #741 |
| Multi-location VA encode fidelity | F23 deepen / new child after M4 |
| Guidance assert gaps vs lint map | Link #800 survivors |
| AIRMET CNL official stem missing | Defer — no vendor stem |

## Out of scope (this dig)

- Hand-edit `vendor/schemas/*`
- Engine encode rewrites
- #806 WIS2
- Committing upstream clones / HTML zips
