# Re-mine pass — early gaps (S043 / EV-035)

**Date:** 2026-08-05  
**Disposition (user):** For all gaps — **re-mine first**; if that fails → **open a ticket**.  
**Decision id:** `D-S043-gaps` = re-mine→ticket

## Gap 1 — VONA encode (Guidance silent)

| Step | Result |
|------|--------|
| Re-mine `TAC-to-XML-Guidance.txt` (2025-2) | **Confirmed empty** — no VONA section (`NO_VONA_IN_GUIDANCE`) |
| Re-mine vendor docs | **Partial success** — promote durable cites: |
| | • `documentation/webpages/AHL.asciidoc` — TAC `WM` / IWXXM `LM` for VONA |
| | • `documentation/manual/FM205.adoc` — VONA package 1.0.0 + `vona.xsd` URL |
| | • `ReleaseNotes-IWXXM.txt` — VONA package RC notes |
| | • Peer `vona-A7-1.{tac,xml}` + `vona.xsd` + SCH (already cookbook SoT) |
| Fail residual | **No product-token encode cookbook in Guidance** — encode remains cookbook + XSD/SCH |

**Ticket:** open — upstream/Guidance-silent VONA encode cookbook residual (track under #846).

## Gap 2 — US REMARKS encode / validate ⚠

| Step | Result |
|------|--------|
| Re-mine iwxxm-us PDF dig + pin XSDs | Encode themes largely ✅ (S032); **validate column still ⚠** |
| Vendor | `iwxxm-us/3.0/*.xsd` present; **no US Schematron package** in pin |
| Fail residual | Validate path for US extensions = WMO base SCH + US XSD only — matrix ⚠ is accurate |

**Ticket:** open — iwxxm_us validate-column provenance / SCH depth (document N/A vs deepen).

## Gap 3 — ISSUE_CATALOG thin cites

| Step | Result |
|------|--------|
| Inventory | **100** codes in `ISSUE_CATALOG.json` |
| Re-mine | Many messages already embed Annex/table tags (`A3-2`, `A5-1`, App 5 §…) but **no machine link** to `RULE_SOURCE_URLS` rows |
| Fail residual | Systematic code↔URL map is the EV-035 provenance deliverable; codes that remain unlinkable after 07 map → per-code or batch ticket |

**Ticket:** open umbrella — ISSUE_CATALOG ↔ RULE_SOURCE_URLS linkage (closes as provenance map greens).

## Gap 4 — Bulletin / non-METAR AHL matrix gaps

| Step | Result |
|------|--------|
| Re-fetch WMO AHL page | **HTTP 200** — v1.0.1 still live (same landing as RULE_SOURCE_URLS) |
| Re-mine vendor `AHL.asciidoc` | T1T2 tables include SPECI `SP`→`LP`, TAF `FC/FT`→`LC/LT`, VONA `WM`→`LM`, etc. |
| Fixtures | AHL fixtures exist for SPECI/TAF (`fixtures/ahl/sp_speci.txt`, `fc_taf_*`) — **matrix “gap” may be stale** for some families |
| Fail residual | Families still `gap` in COVERAGE_MATRIX eight-family table after fixture/CI verify → ticket for bulletin body-split / fixture pack |

**Ticket:** open — COVERAGE_MATRIX bulletin AHL residual families (after 07 matrix refresh).

# Promote in 07-build — **done** (S043 / EV-035)

1. ~~`PROVENANCE_MAP` rows for VONA AHL/FM205/ReleaseNotes cites~~ ✅  
2. ~~Refresh COVERAGE_MATRIX VONA conversion cell~~ ✅ (⚠ Guidance + ✅ AHL/FM205)  
3. ~~ISSUE_CATALOG linkage batch~~ ✅ (100/100 ok|paywall; TC-EV035-002)  
4. ~~Re-score bulletin AHL cells~~ ✅ (matrix cells disposition ok; residual body-split tracked #872)

## Tickets opened (remine residuals)

| Issue | Title | Gap | Status after 07 |
|-------|-------|-----|-----------------|
| [#869](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/869) | VONA: TAC-to-XML-Guidance remains silent — cookbook SoT | 1 | Open — Guidance residual; AHL/FM205 promoted |
| [#870](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/870) | iwxxm_us validate-column ⚠ — no US Schematron in pin | 2 | Open — matrix ⚠ documented |
| [#871](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/871) | ISSUE_CATALOG ↔ RULE_SOURCE_URLS provenance linkage | 3 | **Closeable** when TC-EV035-002 greens (map complete) |
| [#872](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/872) | Bulletin AHL matrix residual families after remine | 4 | Partial — cells refreshed; body-split may remain |

Parent epic: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846).

**Map:** [`docs/domain/rules/PROVENANCE_MAP.md`](../../../domain/rules/PROVENANCE_MAP.md) · CI: `make test-provenance-quality`

## EV-098 follow-on gaps (2026-09-02)

| Gap | Ticket | Note |
|-----|--------|------|
| `CA_ALTIMETER_NOT_OBS` reopen (`A////` vs MANOBS) | #1029 | Quarantine positive fixture; deepen authority before re-close |
| `CA-ECCC-QVACI-VERSION-GAP` | #1028 | No IWXXM 3.0 QVA package under CA_ECCC strict 3.0.0 |
| Fixture cleanup `metar_basic` `9999` | #1029 | Backlog — not a map `gaps[]` row |

