# ICAO EUR Doc 014 — EUR SIGMET and AIRMET Guide (5th Ed. 2023) — focused mining notes

**Status:** working notes (not normative). Verify against the PDF / Annex 3 / schemas.wmo.int pin.  
**Focus of this pass:** full-document extract integrity · SIGMET/AIRMET TAC structure · WMO AHL T1T2 · validity/CNL · IWXXM dual-issuance pointers · EUR regional practice  
**Local PDF + extracts (gitignored):** `.local/reference/icao-eur-doc-14-sigmet-airmet-2023/`

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
| Title | EUR SIGMET and AIRMET Guide |
| Publisher | ICAO EUR/NAT Office (EASPG METG) |
| Official PDF | <https://www.icao.int/sites/default/files/EURNAT/Documents/EUR%20and%20Nat%20Docs/EUR%20Documents/EUR%20Documents/014%20-%20EUR%20SIGMET%20and%20AIRMET%20Guide/EUR-Doc-14-EN-5th-Ed-2023-rev-Dec23-clean.pdf> |
| Pin / edition | **Fifth Edition 2023** (rev Dec 2023; footer “6 Dec 2023”) |
| Pages | **90** PDF pages (extract complete) |
| Local text | `.local/reference/icao-eur-doc-14-sigmet-airmet-2023/fulltext.txt` |
| Date mined | 2026-07-20 |
| Access | **public** |
| Label | **normative-conversion-notes** / regional practice guidance (complements Annex 3 App 6; **not** a substitute for SARPs or XSD/SCH) |

---

## Extract integrity (full length)

| Check | Result |
|-------|--------|
| `PdfReader` page count | **90** |
| `===== PAGE N =====` markers in `fulltext.txt` | **90** (contiguous 1…90) |
| `pages.jsonl` rows | **90** (page ids 1…90) |
| Empty pages | **0** |
| Near-empty (&lt;40 chars) | **0** |
| Total extracted chars | ~145 671 (min 232 / max 3982 / mean ~1619) |
| `fulltext.txt` / `pages.jsonl` size | 148 715 / 152 378 bytes |
| PDF metadata title | `ICAO EUR014 - SIGMET AND AIRMET GUIDE` |
| First page | Cover: “EUR SIGMET AND AIRMET GUIDE / FIFTH EDITION 2023” |
| Last page (PDF p.90) | Appendix G coordination log form (printed footer p. 86) |

Page citations below use **PDF extract page numbers** (`===== PAGE N =====`), not printed content footers (offset ≈ +4 after front matter).

---

## What this source is / is not

| Is | Is not |
|----|--------|
| EUR regional **guide** for MWO preparation/dissemination of SIGMET and AIRMET (TAC + dual IWXXM obligation) | Binding global SARPs (those remain **Annex 3** Ch.7 + App 6) |
| Detailed TAC structure: WMO heading, first line, meteorological elements, CNL, VA/TC conventions | Machine SoT for XSD/Schematron (defers to `http://schemas.wmo.int/iwxxm/`) |
| Large Appendix C **TAC examples** + App A abbreviation list + App B coordinates | Space-weather SIGMET (explicitly out of scope, PDF p.5) |
| EUR header lists pointer (EURNAT site → MET Guidance → Headers) | US `iwxxm_us` national profile |
| Alignment note toward latest Annex 3 amendment; EU Reg 2017/373 AMC sequence-number note | Full IWXXM encode cookbook (use TAC-to-XML-Guidance + vendor pin) |

---

## Document map

| Section | Approx. PDF pages | Relevance |
|---------|-------------------|-----------|
| Cover / amendments / TOC | 1–4 | Edition; Parts 1–4 + Apps A–G |
| Part 1 Introduction | 5–6 | Purpose vs Annex 3 / EUR eANP; dual TAC+IWXXM context |
| Part 2 Responsibilities & coordination | 7–11 | MWO/ATS/pilots; cross-FIR coordination; VAAC |
| Part 3 SIGMET preparation | 12–30 | **Primary TAC lint / convert shape** |
| Part 4 AIRMET preparation | 31–44 | **Primary TAC lint / convert shape** |
| App A Abbreviations | 45–46 | Allowed TAC tokens (decode list) |
| App B Coordinates | 47 | TAC geography reporting |
| App C SIGMET examples | 48–82 | Golden-style TAC fixtures (informative regional) |
| App D Special air-reports | 83–84 | AIREP → SIGMET feed |
| App E–G Coordination LoA / process / stats | 85–90 | Ops (low convert priority) |

---

## Product × artifact matrix

| Product | TAC input artifact | IWXXM output (T1T2 / root) | Official example / guidance in this PDF | Gap vs GIFTs | Consumer |
|---------|--------------------|----------------------------|-----------------------------------------|--------------|----------|
| SIGMET (other) | `WS…` AHL + `CCCC SIGMET … VALID …` | `LS` · `iwxxm:SIGMET` | Part 3 + App C | Entire product outside GIFTs | `tac-validate`, `tac2iwxxm`, bulletin |
| SIGMET VA | `WV…` | `LV` · VA SIGMET | §3.4.3.1.4 + App C | Entire product | same |
| SIGMET TC | `WC…` | `LY` · TC SIGMET | §3.4.3.1.5 + App C | Entire product | same |
| AIRMET | `WA…` | `LW` · `iwxxm:AIRMET` | Part 4 | Entire product | same |
| Bulletin / AHL | Unique header per FIR/CTA/UIR | Same T1T2 family | §3.4.1 / §4.3.1; EUR headers list on EURNAT site | Outside GIFTs | bulletin / F8 |
| Schema pin | — | XSD/SCH at schemas.wmo.int/iwxxm/ | Notes on PDF pp.13, 32 | Prefer **vendor pin** `v2025-2` over bare landing | `iwxxm-validate` |

---

## Key findings

### Dual TAC + IWXXM (PDF pp.12, 31–32)

- MWOs **shall** issue SIGMET/AIRMET in TAC **and** IWXXM; EUR Docs **018** / **020** and WMO-No. **306** Vol I.3 cited for more IWXXM/exchange detail.
- Structure notes: same logical elements apply in IWXXM; **exact** XML formatting → schemas/schematron at `http://schemas.wmo.int/iwxxm/` (prefer pinned `…/iwxxm/<vendor-pin>/` at runtime).
- **Do not use `COR`** for SIGMET corrections: not in Annex 3; **not supported by IWXXM**; unclear to users — cancel + re-issue instead (PDF p.12).

### WMO AHL T1T2 (PDF pp.13–14, 32)

| Role | TAC | IWXXM |
|------|-----|-------|
| SIGMET other | `WS` | `LS` |
| SIGMET VA | `WV` | `LV` |
| SIGMET TC | `WC` | `LY` |
| AIRMET | `WA` | `LW` |

Heading shape: `T1T2A1A2ii CCCC YYGGgg` (WMO-No. 386 tables for `A1A2` / `ii`).

### First line / validity (PDF pp.14–15, 33–34)

- SIGMET: `CCCC SIGMET [n][n]n VALID YYGGgg/YYGGgg CCCC-`
- AIRMET: `CCCC AIRMET [n][n]n VALID YYGGgg/YYGGgg CCCC-`
- Sequence restarts **0001 UTC** daily; up to three symbols (`1`, `01`, `A01`, …). EU Reg **2017/373** AMC: phenomenon-specific `A01`-style only where applicable (PDF p.15).
- Validity caps (aligns Annex 3): **WS ≤ 4 h**; **WC/WV ≤ 6 h**; **AIRMET ≤ 4 h**.
- Midnight boundary: per Annex 5 note — end-of-day → next calendar `YY` with `0000` (PDF pp.14, 32).

### Meteorological body / one phenomenon

- SIGMET met part: ordered element table (location/FIR, TEST|EXER, phenomenon, OBS|FCST, location, level, movement, intensity change, forecast time/position) — PDF p.17+.
- AIRMET: similar table; **no** explicit forecast-position group (Annex 3 does not enable it) — PDF p.43.
- **One phenomenon per message** restated for AIRMET (PDF p.37); SIGMET types split WS/WV/WC (PDF p.13).
- Phenomena interpretation guidance (FRQ/SQL/TSGR/SEV TURB/ICE/MTW/SS/DS thresholds) is **EUR practice** elaborating Annex 3 — useful for operator lint messages, not a substitute for App 6 token lists (PDF pp.18–21).

### Cancellation (PDF pp.28–29, 43–44)

- CNL message: same T1T2 family; next sequence; validity = **remaining** original period; body `CNL SIGMET|AIRMET <seq> <orig VALID>` (+ VA MOV TO FIR when applicable per Annex 3).
- Significant change → cancel + new message (not in-place rewrite).

### Appendices for fixtures

- **App A** — allowed abbreviation/decode list for TAC SIGMET/AIRMET (PDF pp.45–46).
- **App B** — coordinate reporting guidelines (PDF p.47).
- **App C** — extensive SIGMET TAC examples (PDF pp.48–82); treat as **informative regional** fixtures — prefer official `schemas.wmo.int/iwxxm/<pin>/examples/` for CI gates when available.

---

## Catalog paste rows

```text
### ICAO EUR Doc 014 — EUR SIGMET and AIRMET Guide (5th Ed. 2023)
- Publisher: ICAO EUR/NAT (EASPG METG)
- URL: https://www.icao.int/sites/default/files/EURNAT/Documents/EUR%20and%20Nat%20Docs/EUR%20Documents/EUR%20Documents/014%20-%20EUR%20SIGMET%20and%20AIRMET%20Guide/EUR-Doc-14-EN-5th-Ed-2023-rev-Dec23-clean.pdf
- Landing: http://www.icao.int/EURNAT/Pages/welcome.aspx (EUR Documents → 014)
- Access: public
- Applies to: products=[SIGMET,AIRMET]; profiles=[annex3]; role=[validation, conversion, bulletin]
- Gap vs GIFTs: entire SIGMET/AIRMET products; AHL WS/WV/WC/WA ↔ LS/LV/LY/LW; CNL; no COR; EUR examples
- Consumer: tac-validate | tac2iwxxm | bulletin | UI-decode
- Label: normative-conversion-notes (regional guide; Annex 3 remains SARPs SoT)
- Caveats: Complements Annex 3 App 6 / Table A6-1A — do not override SARPs. IWXXM formatting defers to schemas.wmo.int/iwxxm/<pin>/ (vendor manifest). Space weather out of scope. EUR-specific sequence AMC (EU 2017/373) is regional.
- Mined: 2026-07-20 · mining/icao-eur-doc-14-sigmet-airmet-2023-mining-notes.md
```

---

## Domain-knowledge cross-check (defer to latest)

| Older claim (doc + date/edition) | This source finding | Action |
|----------------------------------|---------------------|--------|
| Annex 3 App 6 / Ch.7 validity & phenomena (canonical SoT) | Guide restates ≤4 h / ≤6 h VA-TC and one-phenomenon; adds EUR interpretation thresholds | **Keep Annex 3 as SARPs SoT**; cite guide as regional practice / examples |
| OPMET IWXXM Exchange Guidelines 5th (T1T2 LA…LY) | Same T1T2 mapping for SIGMET/AIRMET (`LS`/`LV`/`LY`/`LW`) | **Consistent** — reinforce bulletin row |
| `schemas.wmo.int/iwxxm/` bare URL in PDF (2023) | Runtime pin is vendor **v2025-2** | **Defer to vendor pin** for XSD/SCH; keep guide for TAC ops prose |
| GIFTs METAR/SPECI-only | Full SIGMET/AIRMET TAC+IWXXM dual issuance | Gap already recorded — guide strengthens F6 backlog |

---

## Implications for this repo

- **tac-validate / TAC_VALIDATION.md:** Cite EUR Doc 014 as **public** regional companion for A6 checklist (AHL, first line, CNL, no COR, validity caps, sequence forms). Fail-closed rules still need Annex 3 when licensed.
- **tac2iwxxm / IWXXM_CONVERSION.md:** Dual-issuance + T1T2 TAC↔IWXXM map; COR unsupported in IWXXM; schema URL → pinned path.
- **iwxxm-validate / IWXXM_VALIDATION.md:** No new schema pins — PDF defers to schemas.wmo.int.
- **bulletin / F8:** Unique header-per-FIR guidance; EUR header list on EURNAT site.
- **Promotion:** Catalog row + light canonical/matrix cites (this pass).

---

## Local extract index

| Extract | Contents |
|---------|----------|
| `fulltext.txt` / `pages.jsonl` | Full 90-page extract |
| `extracts/part3-sigmet-structure.txt` | PDF pp.12–30 |
| `extracts/part4-airmet-structure.txt` | PDF pp.31–44 |
| `extracts/appendix-a-abbreviations.txt` | PDF pp.45–46 |
| `extracts/appendix-b-coordinates.txt` | PDF p.47 |
| `extracts/appendix-c-examples-index.txt` | PDF pp.48–50 (examples continue through ~82) |
| `extracts/iwxxm-mentions.txt` | All IWXXM/XML hit lines |

---

## Suggested next mining passes

1. Deep pass on **Appendix C** examples → candidate informative fixtures for SIGMET lint (label informative; prefer official `examples/` for G6).
2. Fetch/list **EUR SIGMET and AIRMET headers** page from EURNAT MET Guidance (catalog row).
3. Cross-link EUR Doc **018** / **020** if public PDFs exist (exchange/IWXXM regional).
4. Optional: map App A abbreviations ↔ `codes.wmo.int` SigWx/AirWx concept IDs (caveat drift).
