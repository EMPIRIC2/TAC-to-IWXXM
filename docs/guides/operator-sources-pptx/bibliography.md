# Bibliography — curated sources for the briefing deck

Subset of [RULE_SOURCE_URLS.md](../../domain/rules/RULE_SOURCE_URLS.md) plus software
cites. Labels: **normative** | **normative-schema** | **normative-vocabulary** |
**informative** | **software**. Access: **public** | **paywall** | **library**.

Vendor pin (runtime): IWXXM **v2025-2**, codelists **49-2**, iwxxm-us **3.0** —
[`vendor/manifest.json`](../../../vendor/manifest.json).

---

## A. ICAO / WMO / NWS (domain)

| Title | URL | Label | Access | Use on slides |
|-------|-----|-------|--------|---------------|
| ICAO Annex 3 — Meteorological Service for International Air Navigation | https://store.icao.int/en/annexes/annex-3 | normative | paywall | 2, 3, 12 |
| ICAO Doc 8896 — Manual of Aeronautical Meteorological Practice | https://store.icao.int/en/manual-of-aeronautical-meteorological-practice-doc-8896 | normative (practice) | paywall | 3 |
| ICAO Doc 10003 — Manual on the ICAO Meteorological Information Exchange Model | ICAO Store (see RULE_SOURCE_URLS) | normative | paywall | 3, 9 |
| ICAO EUR Doc 014 — EUR SIGMET and AIRMET Guide (5th Ed. 2023) | https://www.icao.int/sites/default/files/EURNAT/Documents/EUR%20and%20Nat%20Docs/EUR%20Documents/EUR%20Documents/014%20-%20EUR%20SIGMET%20and%20AIRMET%20Guide/EUR-Doc-14-EN-5th-Ed-2023-rev-Dec23-clean.pdf | normative-conversion-notes (regional) | public | 3 |
| Guidelines for the Implementation of OPMET Data Exchange using IWXXM (5th Ed.) | https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf | normative-conversion-notes | public | 2, 5, 12 |
| WMO-No. 306 Vol I.3 — Manual on Codes Part D | https://library.wmo.int/idurl/4/35769 | normative (FM 205) | library | 3, 5 |
| IWXXM schemas (2025-2) | https://schemas.wmo.int/iwxxm/2025-2/ | normative-schema | public | 3, 6, 12 |
| WMO codes registry | https://codes.wmo.int/ | normative-vocabulary | public | 3, 12 |
| Community IWXXM / AHL | https://community.wmo.int/en/activity-areas/wis/iwxxm · AHL: https://community.wmo.int/en/activity-areas/wis/iwxxm/ahl-icao-data | informative index | public | 5, 10 |
| wmo-im/iwxxm GitHub | https://github.com/wmo-im/iwxxm (tag **v2025-2**) | normative-schema | public | 6, 12 |
| wmo-im/iwxxm-codelists | https://github.com/wmo-im/iwxxm-codelists (tag **49-2**) | normative-vocabulary | public | 6 |
| wmo-im/iwxxm-modelling | https://github.com/wmo-im/iwxxm-modelling (tag **v2025-2**) | informative/modelling | public | 6 |
| wmo-im/iwxxm-translation | https://github.com/wmo-im/iwxxm-translation | informative (parity) | public | 6 |
| IWXXM-US 3.0 schemas | https://nws.weather.gov/schemas/iwxxm-us/ (tarball per manifest) | normative-schema (US) | public | 3, 6 |
| FMH-1 (2019) Federal Meteorological Handbook No. 1 | OFCM/ICAMS public PDF (see RULE_SOURCE_URLS / fmh1 mining notes) | normative (US TAC) | public | 3 |
| PPT-02 IWXXM Framework (TT-AvData / ESAF workshop) | https://www.icao.int/filebrowser/download/26741?fid=26741 | informative | public | 10 |

Mining digs (working notes, not SoT): [docs/domain/mining/](../../domain/mining/).

---

## B. In-repo standing docs (give to technical audience)

| Doc | Path | Role |
|-----|------|------|
| Domain hub / pipeline | [docs/domain/README.md](../../domain/README.md) | Stage table |
| URL catalog | [docs/domain/rules/RULE_SOURCE_URLS.md](../../domain/rules/RULE_SOURCE_URLS.md) | Master landings |
| Access policy | [docs/domain/rules/ACCESS_AND_CITATION.md](../../domain/rules/ACCESS_AND_CITATION.md) | Paywall rules |
| Provenance index | [docs/domain/rules/PROVENANCE_MAP.md](../../domain/rules/PROVENANCE_MAP.md) | Dig ↔ rule |
| Issue codes | [docs/domain/rules/ISSUE_CATALOG.md](../../domain/rules/ISSUE_CATALOG.md) | Lint codes |
| Operator runbook | [docs/ops/operator-ui-runbook.md](../../ops/operator-ui-runbook.md) | Day-to-day ops |
| Product features | [docs/feature-list.md](../../feature-list.md) | F7/F9/F10… |
| Architecture | [docs/spec.md](../../spec.md) | Components |
| Dependencies | [docs/dependency-inventory.md](../../dependency-inventory.md) | Stack |

---

## C. Software stack (high level)

| Component | Cite | Label |
|-----------|------|-------|
| FastAPI / uvicorn | dependency-inventory · apps/backend | software |
| React 18 + Vite + TypeScript | dependency-inventory · apps/frontend | software |
| CodeMirror 6 | F7 editor choice | software |
| msgspec | ADR-026 HTTP DTOs | software |
| packages/tac-validate | F12 / F15 | software |
| packages/tac2iwxxm | F6 / F14 | software |
| packages/iwxxm-validate | F2 / F13 | software |
| packages/dissemination | F16–F19 / ADR-030 | software |
| Supabase Auth (JWT only) | F31 / ADR-033 | software |
| DigitalOcean Postgres / DOKS | F30 | software |

[Corpus: tech-spec] [docs/dependency-inventory.md]
