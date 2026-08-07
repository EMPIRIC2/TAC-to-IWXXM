# Slide outline — TAC-to-IWXXM sources briefing

Copy each block into one slide. Speaker notes are for presenter view only.

---

## Slide 1 — Title

**Title:** TAC → IWXXM Operator System  
**Subtitle:** Built from ICAO / WMO / NWS sources · Runtime pin **IWXXM v2025-2**

**Bullets (optional footer):**

- Repository: EMPIRIC2/TAC-to-IWXXM (monorepo)
- Briefing pack: `docs/guides/operator-sources-pptx/`

**Speaker notes:** This deck is about *provenance* — which standards and schema pins
underwrite the tool — not a feature tour. Operator click-paths live in
`docs/ops/operator-ui-runbook.md`. [Corpus: product §F7] [Corpus: system-spec]

**Figure:** none (or org logo only)

**Sources:** vendor/manifest.json · feature-list F7

---

## Slide 2 — Why IWXXM (problem framing)

**Title:** TAC presentation vs IWXXM exchange

**Bullets:**

- TAC remains familiar for human presentation
- IWXXM (XML/GML) is the structured exchange form for OPMET
- Annex 3 frames dual TAC + IWXXM obligations (cite; do not quote)
- Operators need software to lint TAC, encode IWXXM, and validate XSD + Schematron

**Speaker notes:** Informative workshop framing (PPT-02) says consumers still render TAC
often while exchange moves to IWXXM. Do not claim TAC sunset dates as binding unless
citing a current SARPs edition. [docs/domain/mining/PPT-02-…] [Corpus: product]

**Figure:** optional simple two-column diagram “TAC text” ↔ “IWXXM XML” (draw yourself)

**Sources:** ICAO Annex 3 (paywall store landing) · PPT-02 informative · OPMET Guidelines 5th (public)

---

## Slide 3 — Standards map

**Title:** Standards & registries we built from

**Bullets:**

- **ICAO Annex 3** — TAC SARPs / templates — *Access: paywall*
- **WMO-No. 306 Vol I.3** — Manual on Codes / FM 205 representations — *library*
- **codes.wmo.int** — linked-data vocabularies — *public*
- **schemas.wmo.int/iwxxm** — XSD + Schematron landings — *public*
- **FMH-1 / iwxxm-us** — US METAR/SPECI REMARKS overlay — *public*
- **EUR Doc 014** — SIGMET/AIRMET guide — *public PDF*

**Speaker notes:** Full catalog: RULE_SOURCE_URLS.md. Paywalled prose never lives in the
repo. [docs/domain/rules/RULE_SOURCE_URLS.md] [ACCESS_AND_CITATION.md]

**Figure:** see image-pointers §Standards logos / landings table (screenshot of landings list OK)

**Sources:** RULE_SOURCE_URLS §1–§3

---

## Slide 4 — What we implemented (architecture)

**Title:** Monorepo components

**Bullets:**

- `apps/frontend` — operator workbench (React / Vite)
- `apps/backend` — FastAPI convert / lint / validate / decode
- `apps/worker` — near-RT ingest (F8; not auto-disseminate)
- `packages/tac-validate` · `tac2iwxxm` · `iwxxm-validate`
- `vendor/schemas/*` — read-only WMO / NWS snapshots

**Speaker notes:** Redraw from spec.md runtime diagram. Auth optional for long-term
sessions only (F21/F31). [Corpus: system-spec] [Corpus: product §F21/F31]

**Figure:** architecture box diagram — **draw from** image-pointers §Architecture (mermaid in pack)

**Sources:** docs/spec.md §System Architecture · docs/CORPUS.md

---

## Slide 5 — Build pipeline (TAC → validated IWXXM)

**Title:** Seven-stage domain pipeline

**Bullets:**

1. TAC lint (Annex 3 / vocab)
2. Convert (encode + nilReasons)
3. Well-formed XML
4. XSD (structure)
5. Schematron (+ offline RDF)
6. Golden example pairs
7. Bulletin / AHL / ops (when used)

**Speaker notes:** Stages must stay separate — Schematron pass ≠ Annex 3 SARPs proof.
Hub table in docs/domain/README.md. Engines: tac-validate → tac2iwxxm → iwxxm-validate.

**Figure:** horizontal pipeline arrows (draw) — image-pointers §Pipeline

**Sources:** docs/domain/README.md · TAC_VALIDATION / IWXXM_CONVERSION / IWXXM_VALIDATION

---

## Slide 6 — Vendor / upstream pins

**Title:** Runtime schema pins

**Bullets:**

- `wmo-im/iwxxm` **v2025-2**
- `wmo-im/iwxxm-codelists` **49-2**
- `wmo-im/iwxxm-modelling` **v2025-2**
- `iwxxm-translation` — informative parity only
- `iwxxm-us` **3.0** (NWS)

**Speaker notes:** Pins are in vendor/manifest.json with SHAs. Conflict rule: defer to pin
over older printed package tables. Supported operator window typically Latest + Previous
(2025-2 + 2023-1). [Corpus: system-spec] vendor · VERSION_SUPPORT_POLICY

**Figure:** screenshot of `vendor/manifest.json` keys (redact nothing secret — file is public) OR table

**Sources:** vendor/manifest.json · schemas.wmo.int/iwxxm/2025-2/

---

## Slide 7 — Operator UI (capability → feature)

**Title:** Operator workbench surfaces

**Bullets:**

- Multi-product workbench + sessions — **F7**
- Value-aware decode + summary — **F9**
- Live IWXXM preview / lint UX — **F10**
- Golden / official examples — **F7.g**
- Optional dissemination drawer — **F16–F19**
- Public convert; optional Auth for storage — **F21 / F31**

**Speaker notes:** This slide is the only “UI” slide — keep it capability-mapped, not a
click tutorial. Screenshots from *local* non-deployed preview preferred.
[Corpus: product] [docs/ops/operator-ui-runbook.md]

**Figure:** 1–2 local UI screenshots (optional) — image-pointers §UI

**Sources:** feature-list F7/F9/F10 · S011 session brief

---

## Slide 8 — Rule provenance story

**Title:** From dig → rule → operator message

**Bullets:**

- Mine public / licensed sources → `docs/domain/mining/*`
- Promote durable cites → RULE_SOURCE_URLS + canonical strategy docs
- ISSUE_CATALOG codes link operators to sources
- PROVENANCE_MAP indexes dig ↔ rule ↔ source
- UI lint catalog shows WMO/ICAO/IWXXM attribution

**Speaker notes:** S043/EV-035 built standing provenance; EV-040 surfaced attribution in UI.
Gaps are labeled `gap` / `paywall` — never silently invented. [docs/domain/rules/PROVENANCE_MAP.md]

**Figure:** simple flow Dig → Catalog → Lint console (draw)

**Sources:** PROVENANCE_MAP · ISSUE_CATALOG · RULE_SOURCE_URLS

---

## Slide 9 — Access friction

**Title:** What operators can open freely

**Bullets:**

| Class | Examples | In-repo handling |
|-------|----------|------------------|
| Paywall | Annex 3, Doc 10003 | Cite store URL only |
| Library / captcha | WMO-306 | Mining notes + gitignored `.local/` |
| Public machine | schemas / codes / EUR Doc 014 | Prefer for CI + goldens |
| Informative | PPT-02 workshop deck | Corroboration only |

**Speaker notes:** ACCESS_AND_CITATION.md is the standing policy. Unofficial mirror PDFs are
not SoT. [docs/domain/rules/ACCESS_AND_CITATION.md]

**Figure:** none (table is the figure)

**Sources:** ACCESS_AND_CITATION.md

---

## Slide 10 — Informative workshop corroboration (PPT-02)

**Title:** WMO TT-AvData “IWXXM Framework” (workshop)

**Bullets:**

- Public ICAO filebrowser deck (ESAF workshop, 2025-10-22)
- Convenient pointer cluster to WMO + ICAO landings
- Package × IWXXM-line matrix — **informative**; prefer vendor XSD versions
- Translation attrs + `translationFailedTAC` reminder

**Speaker notes:** Label every claim **informative**. Full dig:
docs/domain/mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md. Local slide PNGs under
`.local/reference/ppt-02-…/extracts/slide-images/` — **do not commit**. Official download:
https://www.icao.int/filebrowser/download/26741?fid=26741

**Figure:** optional *personal* extract of PPT-02 slides 6–7 landings (cite deck) — not for git

**Sources:** PPT-02 mining notes · ICAO filebrowser URL

---

## Slide 11 — Software stack (high level)

**Title:** Implementation stack

**Bullets:**

- Python 3.12 · FastAPI · msgspec HTTP DTOs
- React 18 · Vite · TypeScript · CodeMirror 6
- `tac-validate` / `tac2iwxxm` / `iwxxm-validate` workspace packages
- Optional Rust core in iwxxm-validate path (F13)
- DigitalOcean Postgres + Supabase Auth (JWT) · DOKS deploy target

**Speaker notes:** Details in dependency-inventory.md — do not dump every pin on the slide.
GIFTs removed at F6 cutover (ADR-014). [Corpus: tech-spec]

**Figure:** none or small stack icons (optional)

**Sources:** docs/dependency-inventory.md · docs/tech-spec.md

---

## Slide 12 — Bibliography / further reading

**Title:** Landings to keep

**Bullets (short URLs on slide; full table in bibliography.md):**

- https://schemas.wmo.int/iwxxm/2025-2/
- https://codes.wmo.int/
- https://github.com/wmo-im/iwxxm (tag v2025-2)
- ICAO Annex 3 store listing (paywall)
- OPMET IWXXM Exchange Guidelines 5th (public PDF)
- Repo: `docs/domain/rules/RULE_SOURCE_URLS.md`

**Speaker notes:** Hand out bibliography.md or link the repo path. Remind: purchase ICAO
docs for normative prose. Operator runbook for day-to-day use.

**Figure:** none

**Sources:** bibliography.md
