# Domain mining notes (transitory)

Working notes from `mine-domain-sources` / `extract-pdf-to-repo` passes.

**Not SoT.** Promote lasting citations into:

- [`../TAC_VALIDATION.md`](../TAC_VALIDATION.md)
- [`../IWXXM_CONVERSION.md`](../IWXXM_CONVERSION.md)
- [`../IWXXM_VALIDATION.md`](../IWXXM_VALIDATION.md)
- [`../rules/RULE_SOURCE_URLS.md`](../rules/RULE_SOURCE_URLS.md)
- [`../rules/COVERAGE_MATRIX.md`](../rules/COVERAGE_MATRIX.md)
- [`../rules/PROVENANCE_MAP.md`](../rules/PROVENANCE_MAP.md) (+ JSON twin) — dig index CI (S043 / EV-035)
- [`../profiles/`](../profiles/) — **semantic + exchange profile source catalog** (EV-063 / F35–F36; #913)

Local binaries / full extracts: `.local/reference/<slug>/` (gitignored).

| Notes | Focus |
|-------|-------|
| [wmo-im-iwxxm-IWXXM-tree-mining-notes.md](./wmo-im-iwxxm-IWXXM-tree-mining-notes.md) | #804 — `IWXXM/` folder relevancy + official examples stem×surface matrix (S031/EV-024) |
| [iwxxm-us-metar-speci-pdf-mining-notes.md](./iwxxm-us-metar-speci-pdf-mining-notes.md) | #773 — IWXXM-US METAR/SPECI PDF + MDL type×TAC×encode checklist (S031/EV-024) |
| [iwxxm-2025-2-reference-set-mining-notes.md](./iwxxm-2025-2-reference-set-mining-notes.md) | Progress tracker for IWXXM validation/conversion reference inventory (§1–§6) |
| [awc-data-api-mining-notes.md](./awc-data-api-mining-notes.md) | NOAA AWC Data API — live TAC/IWXXM fixtures (informative) |
| [community-wmo-iwxxm-wayback-mining-notes.md](./community-wmo-iwxxm-wayback-mining-notes.md) | Community IWXXM home via Wayback — package×Amd compatibility table |
| [wmo-im-org-mining-notes.md](./wmo-im-org-mining-notes.md) | Org survey `github.com/wmo-im` |
| [wmo-im-tier-a-mining-notes.md](./wmo-im-tier-a-mining-notes.md) | Local Tier A clones / pin drift |
| [wmo-im-tier-b-mining-notes.md](./wmo-im-tier-b-mining-notes.md) | Local Tier B (collect, WIS2*, GTStoWIS2, CCT, foundation pkgs) |
| [iwxxm-modelling-v2025-2-mining-notes.md](./iwxxm-modelling-v2025-2-mining-notes.md) | UML/EA generators |
| [WMO-306-vI-3-2023-mining-notes.md](./WMO-306-vI-3-2023-mining-notes.md) | Manual on Codes Vol I.3 / FM 205 |
| [WMO-306-vI-3-2019-upd-2021-mining-notes.md](./WMO-306-vI-3-2019-upd-2021-mining-notes.md) | Manual on Codes Vol I.3 (2019/upd-2021) — historical; dig **1–272 complete** (FM 205-2018 + D-1…D-10) · #798 |
| [OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md](./OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) | ICAO OPMET exchange Guidelines 5th |
| [icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md](./icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md) | ICAO EUR Doc 014 (5th Ed. 2023): EUR SIGMET/AIRMET Guide — TAC structure, AHL, CNL, dual IWXXM |
| [PPT-02-IWXXM-Framework-WMO-mining-notes.md](./PPT-02-IWXXM-Framework-WMO-mining-notes.md) | Informative workshop deck (TAC↔IWXXM + package matrix) |
| [ICAO-Doc-10003-draft-2014-mining-notes.md](./ICAO-Doc-10003-draft-2014-mining-notes.md) | Historical Doc 10003 Advance 2014 |
| [icao-annex-3-mining-notes.md](./icao-annex-3-mining-notes.md) | ICAO Annex 3 (20th + Amd 81): F6 SARPs; SPECI/TAF thresholds; TREND; SIGMET/AIRMET; IWXXM shall; App 2 VAA/TCA templates |
| [fmh1-2019-mining-notes.md](./fmh1-2019-mining-notes.md) | US FMH-1 (2019): METAR/SPECI body + RMK §12; US SPECI criteria — profile `iwxxm_us` |
| [schemas-wmo-int-metce-mining-notes.md](./schemas-wmo-int-metce-mining-notes.md) | METCE foundation schemas at schemas.wmo.int/metce (1.0–1.2) |
| [schemas-wmo-int-opm-mining-notes.md](./schemas-wmo-int-opm-mining-notes.md) | OPM Observable Property Model at schemas.wmo.int/opm (1.0–1.2) |
| [schemas-wmo-int-saf-mining-notes.md](./schemas-wmo-int-saf-mining-notes.md) | SAF (Simple Aeronautical Features) at schemas.wmo.int/saf (1.0–1.1; deprecated) |
| [schemas-wmo-int-tsml-mining-notes.md](./schemas-wmo-int-tsml-mining-notes.md) | OGC TimeseriesML (TSML) 1.0 mirror at schemas.wmo.int/tsml — not on IWXXM F6 path |
| [schemas-wmo-int-rule-mining-notes.md](./schemas-wmo-int-rule-mining-notes.md) | Centralized Schematron index at schemas.wmo.int/rule (1.0–1.2; not IWXXM pin path) |
| [icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md](./icao-apac-iwxxm-faqs-3rd-2025-mining-notes.md) | ICAO APAC IWXXM FAQs 3rd Ed. (Mar 2025) — translation/NSC/COLLECT gotchas · #797 |
| [manobs-manair-ca-mining-notes.md](./manobs-manair-ca-mining-notes.md) | EV-064 / #916 — MANOBS/MANAIR TAC rules for `CA_ECCC` |
| [eccc-iwxxm-ca-mining-notes.md](./eccc-iwxxm-ca-mining-notes.md) | EV-064 / #916 — ECCC IWXXM 3.0.0 + `*-ca.xsd` + code-ca + datamart |
| [codes-wmo-int-aviation-mining-notes.md](./codes-wmo-int-aviation-mining-notes.md) | codes.wmo.int aviation registers (colour/nil/MetFeature 28 vs 27; 4678 CSV=402 vs HTML≈101; SCH RDF match) · #797 |
| [vona-encode-remine-ev035-mining-notes.md](./vona-encode-remine-ev035-mining-notes.md) | S043/EV-035 remine — VONA Guidance silent; AHL WM/LM + FM205 promotes · #869 |
