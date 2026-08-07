# Citation & search guide — national compliance briefing

> **Audience:** MET / aviation authority leadership (State / ANSP / Met Service heads)  
> **Purpose:** Find **citable** ICAO/WMO landings for “why we must produce IWXXM” and “what good looks like” — without inventing deadlines or pasting paywalled SARPs text.  
> **Policy:** [ACCESS_AND_CITATION.md](../../domain/rules/ACCESS_AND_CITATION.md)  
> **Master URL catalog:** [RULE_SOURCE_URLS.md](../../domain/rules/RULE_SOURCE_URLS.md)

Use this before finalizing slides. Prefer **landing pages + edition + section numbers** over long quotations.

---

## 1. What you can safely claim (and what you must not)

| Claim type | Safe approach | Do not |
|------------|---------------|--------|
| States must provide MET service under Annex 3 | Cite **ICAO Annex 3** store listing + edition you hold | Paste Annex 3 body into the deck |
| OPMET is exchanged as IWXXM (XML/GML) as well as TAC practice | Cite Annex 3 + **Doc 10003** + public **OPMET IWXXM Exchange Guidelines 5th** | Equate Guidelines with Annex 3 SARPs |
| Produced IWXXM should validate XSD **and** Schematron | Cite Guidelines §5.3.2 (public PDF) + `schemas.wmo.int/iwxxm/<pin>/` | Claim “compliant” from convert alone |
| Encoding model / FM 205 | Cite **WMO-No. 306 Vol I.3** library landing | Treat workshop PPT as SoT |
| Operational schema line | Cite vendored pin **v2025-2** + https://schemas.wmo.int/iwxxm/2025-2/ | Invent a sunset date unless your licensed SARPs edition says it |
| TAC sunset ~2030 | Only as **informative** workshop messaging (PPT-02) with caveat | Present as binding Annex 3 text without checking your edition |

---

## 2. Priority cite list (leaders’ handout)

| # | Cite as | URL | Access | Role |
|---|---------|-----|--------|------|
| 1 | ICAO, *Annex 3 — Meteorological Service for International Air Navigation* (current Store edition) | https://store.icao.int/en/annexes/annex-3 | **Paywall** | SARPs / TAC templates — **normative** |
| 2 | ICAO, *Doc 10003 — Manual on the ICAO Meteorological Information Exchange Model* | https://store.icao.int/en/manual-on-the-icao-meteorological-information-exchange-model-doc-10003 | **Paywall** | IWXXM exchange model — **normative** |
| 3 | ICAO METP, *Guidelines for the Implementation of OPMET Data Exchange using IWXXM* (5th Edition, Oct 2023) | https://www.icao.int/sites/default/files/METP/Documents/Guidlines-for-the-Implementation-of-OPMET-Data-Exchange-using-IWXXM_5th-Edition.pdf | **Public** | Prep, translation, AMHS/FTBP, XSD+SCH — **guidelines** |
| 4 | WMO, *Manual on Codes*, Vol. I.3 (Part D / FM 205 IWXXM) | https://library.wmo.int/idurl/4/35769 | **Library** | Code forms / IWXXM representations — **normative** |
| 5 | WMO IWXXM schemas (pin **2025-2**) | https://schemas.wmo.int/iwxxm/2025-2/ | **Public** | XSD, Schematron, examples — **schema** |
| 6 | WMO codes registry | https://codes.wmo.int/ | **Public** | Vocabularies — **schema** |
| 7 | wmo-im/iwxxm GitHub tag `v2025-2` | https://github.com/wmo-im/iwxxm | **Public** | Schema development tree — **schema** |
| 8 | ICAO EUR Doc 014 — EUR SIGMET and AIRMET Guide (5th Ed. 2023) | See [RULE_SOURCE_URLS.md](../../domain/rules/RULE_SOURCE_URLS.md) EUR Doc 014 row | **Public** | Regional SIGMET/AIRMET — **guidelines** (does not override Annex 3) |
| 9 | PPT-02 *IWXXM Framework* (TT-AvData / ESAF, 22 Oct 2025) | https://www.icao.int/filebrowser/download/26741?fid=26741 | **Public** | Briefing overview — **informative only** |
| 10 | This tool’s runbook + provenance | `docs/ops/operator-ui-runbook.md` · `docs/domain/rules/` | Repo | Software ↔ sources map |

Repo digs (help find section numbers; not SoT):  
`docs/domain/mining/icao-annex-3-mining-notes.md` · `OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md` · `WMO-306-vI-3-2023-mining-notes.md`

---

## 3. Search walkthrough

### A. “Is IWXXM required / how do States exchange OPMET?”

1. ICAO Store → search **“Annex 3”** → open the **edition your State has adopted**.  
2. In-PDF search: `IWXXM`, `XML`, `digital`, `dissemination`, `METAR`, `TAF`, `SIGMET`.  
3. Record **chapter / appendix / table** numbers on slides — not paragraphs.  
4. Download **OPMET IWXXM Exchange Guidelines 5th** (table #3) → search `translation`, `Schematron`, `AMHS`, `FTBP`.  
5. Store search **“Doc 10003”** → use the **published** edition (not the 2014 advance draft).

### B. “What schema version should we validate against?”

1. https://schemas.wmo.int/iwxxm/ → open the year line agreed with your ROC/Region (this tool defaults to **2025-2**).  
2. Confirm ReleaseNotes + `rule/iwxxm.sch` + `examples/`.  
3. Cite: `https://schemas.wmo.int/iwxxm/2025-2/` + GitHub tag `v2025-2`.

### C. “How do we prove a bulletin is exchange-ready?”

1. Guidelines 5th → generation / translation / validation (repo dig: §5.3 — XSD **and** Schematron).  
2. Pipeline: TAC lint → convert → XSD → Schematron.  
3. Official examples: `…/2025-2/examples/` and `vendor/schemas/iwxxm/`.

### D. Regional SIGMET / AIRMET / AHL

1. EUR Doc 014 (public PDF).  
2. AHL: https://community.wmo.int/en/activity-areas/wis/iwxxm/ahl-icao-data  
3. Say: regional guides **complement** Annex 3; they do not replace it.

### E. US national REMARKS

1. FMH-1 (public). 2. IWXXM-US 3.0 (NWS). 3. Label as **national overlay**.

### Web search strings

```
ICAO Annex 3 Meteorological Service site:store.icao.int
ICAO Doc 10003 Meteorological Information Exchange Model
"OPMET Data Exchange using IWXXM" Guidelines 5th Edition filetype:pdf
site:schemas.wmo.int iwxxm 2025-2
WMO Manual on Codes Volume I.3 FM 205
site:library.wmo.int Manual on Codes I.3
ICAO EUR Doc 014 SIGMET AIRMET Guide
IWXXM Framework TT-AvData ESAF workshop
```

---

## 4. Spoken citation patterns

- “Per **ICAO Annex 3** [edition on file], MET service SARPs include the TAC templates we lint against — full text is in the Store edition your State adopted.”  
- “**OPMET exchange in IWXXM** is described in ICAO’s public **OPMET IWXXM Exchange Guidelines, 5th Edition (2023)** — including translation practice and validation against schema and Schematron.”  
- “The digital exchange model is in **ICAO Doc 10003** (Store).”  
- “Machine validation uses WMO IWXXM **2025-2** at schemas.wmo.int; this system pins that line in `vendor/manifest.json`.”  
- “Workshop decks (TT-AvData PPT-02) are **informative**; obligations defer to Annex 3 / Doc 10003 / regional agreements.”

---

## 5. Compliance need → software → source

| Leadership concern | Tool | Cite |
|--------------------|------|------|
| Produce IWXXM from national TAC | `tac2iwxxm` + UI | Guidelines 5th · TAC-to-XML-Guidance · Annex 3 |
| Reject bad TAC | `tac-validate` | Annex 3 · WMO-306 · ISSUE_CATALOG |
| Prove exchange-ready XML | `iwxxm-validate` XSD+SCH | schemas.wmo.int/2025-2 · Guidelines §5.3.2 |
| Multi-product OPMET | F6/F7 products | Annex 3 apps · COVERAGE_MATRIX |
| Trace a rule | Lint catalog attribution | RULE_SOURCE_URLS · PROVENANCE_MAP |
| Bulletin / AHL | AHL/COLLECT modes | Guidelines · community AHL |

Staff: [operator-ui-runbook.md](../../ops/operator-ui-runbook.md).  
Ops notes: [ICAO_OPMET_COMPLIANCE.md](../../domain/iwxxm/ICAO_OPMET_COMPLIANCE.md).

---

## 6. Leave-behind one-pager

1. Annex 3 (Store) — SARPs  
2. Doc 10003 (Store) — exchange model  
3. OPMET IWXXM Guidelines 5th (public PDF) — how to implement exchange  
4. schemas.wmo.int/iwxxm/2025-2 — validate here  
5. codes.wmo.int — vocabularies  
6. This system: lint → convert → XSD+SCH against pin v2025-2  

[Corpus: product §F6/F7] [docs/domain/rules/ACCESS_AND_CITATION.md]
