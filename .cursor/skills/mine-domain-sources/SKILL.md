---
name: mine-domain-sources
description: >
  Mines authoritative TAC validation, TAC→IWXXM conversion, and IWXXM validation
  sources into docs/domain/ (URL catalogs, coverage matrices, focused mining notes).
  Use when the user asks to mine a URL/repo/registry for domain rules, expand
  RULE_SOURCE_URLS, update Annex3/IWXXM creation/validation source docs, or continue
  ticket-style discovery (e.g. #719) with results as issue comments and/or tracked notes.
---

# Mine domain sources → `docs/domain/`

Discovery / documentation skill for **rule provenance**. Produce citations, matrices, and
working notes — **not** engine rewrites, **not** copyrighted full-text dumps.

Complements [extract-pdf-to-repo](../extract-pdf-to-repo/SKILL.md) (PDF binary → `.local/` +
notes). Use **this** skill for web/GitHub/registry/vendor mining and for promoting findings
into the standing domain catalog.

## When to use

- User provides a URL, WMO/ICAO landing, `codes.wmo.int` register, or `wmo-im/*` repo
- Expand or refresh `docs/domain/rules/` / `validation/` / `iwxxm/*_SOURCES.md`
- Ticket work that asks for mining comments (e.g. rule-source inventory tickets)
- Map products (METAR…TCA) × (validation | conversion | iwxxm-validation)

## Destinations

| Output | Path |
|--------|------|
| Master URL catalog | `docs/domain/rules/RULE_SOURCE_URLS.md` |
| Coverage matrix | `docs/domain/rules/COVERAGE_MATRIX.md` |
| Access / citation policy | `docs/domain/rules/ACCESS_AND_CITATION.md` (edit only if policy changes) |
| Index / labeling | `docs/domain/rules/README.md` |
| TAC validation sources | `docs/domain/validation/ANNEX3_TAC_VALIDATION_SOURCES.md` |
| TAC→IWXXM creation | `docs/domain/iwxxm/IWXXM_CREATION_SOURCES.md` |
| IWXXM XSD/SCH landings | `docs/domain/iwxxm/IWXXM_VALIDATION_SOURCES.md` |
| Focused working notes | `docs/domain/iwxxm/<slug>-mining-notes.md` or `docs/domain/<topic>/` |
| Issue comments | Linked ticket (optional deliverable) |

**Do not:** invent new `[Corpus]` members; put domain deep-dives under `docs/domain/` only
(see `docs/CORPUS.md` — `domain/` is not minimal corpus).

Prefer **vendor pins** as runtime truth: `vendor/manifest.json` (active IWXXM line, e.g.
`v2025-2`). Prefer `https://schemas.wmo.int/iwxxm/<pin>/` over outdated printed package tables.

## Workflow

Copy and track:

```
- [ ] 1. Scope — URL(s), products, role(s), ticket link
- [ ] 2. Classify source (see source-classes.md)
- [ ] 3. Mine — fetch / gh / vendor mirror; no full PDF scrape into git
- [ ] 4. Draft findings (matrices + catalog paste rows)
- [ ] 5. Publish — issue comment(s) and/or update tracked docs
- [ ] 6. Cross-link companions + set Updated date
- [ ] 7. Commit only if user asks
```

### 1. Scope

Confirm (infer from ticket/user when clear):

| Field | Example |
|-------|---------|
| Source URL(s) | `https://github.com/wmo-im/iwxxm` |
| Products | F6 set: AIRMET · METAR · SIGMET · SPECI · TAF · VAA · TCA (+ SWX/VONA/WAFS if relevant) |
| Role | `validation` · `conversion` · `iwxxm-validation` · `bulletin` |
| Profile | `annex3` · `iwxxm_us` |
| Deliverable | issue comments · catalog update · mining-notes.md · all |
| Ticket | `#719` etc. |

If the source is a **PDF**, hand off binary ingest to **extract-pdf-to-repo**, then continue
here for catalog promotion.

### 2. Classify

Read [source-classes.md](source-classes.md). Assign **label**:

`normative` | `normative-vocabulary` | `normative-schema` | `normative-conversion-notes` |
`normative-examples` | `normative-exchange` | `informative` | `historical-GIFTs`

Record **access**: public / register / captcha / **paywall**.

### 3. Mine

| Kind | How |
|------|-----|
| GitHub repo | `gh api` / clone; prefer **tag matching** `vendor/manifest.json`; use local `vendor/schemas/*` when already pinned |
| schemas.wmo.int | HTTP fetch of landing + example listing; cite pin version |
| codes.wmo.int | Linked Data / CSV download of **registers only**; cite URIs — do not dump full registries into docs |
| Vendor tree | Read-only under `vendor/schemas/` (XSD, `TAC-to-XML-Guidance.txt`, examples, RDF) |
| Paywalled ICAO/WMO PDF | Cite store/library landing + edition; if user has a local PDF, use extract-pdf-to-repo → `.local/` |
| Community / translation fixtures | Mine, but label **informative** |

Always capture for each finding: **publisher**, **stable URL**, **date mined**, **products**,
**role**, **gap vs GIFTs**, **consumer** (`tac-validate` \| `tac2iwxxm` \| `iwxxm-validate` \|
`UI-decode` \| `bulletin`).

### 4. Draft

**Catalog row** — use the template already in `RULE_SOURCE_URLS.md` (also
[catalog-row-template.md](catalog-row-template.md)).

**Product matrix** — when mining a converter/schema source, prefer:

| Product | TAC input artifact | IWXXM output (root / XSD) | Official example / guidance | Gap vs GIFTs | Consumer |

**Mining notes** — use [notes-template.md](notes-template.md) for deep single-source passes.

### 5. Publish

**Issue comments** (when ticket asks for comments):

1. Overview comment (what source is / is not + landings)
2. Product × file or register matrix
3. Conversion/validation highlights + paste-ready catalog rows

Keep comments evidence-based; link vendor paths and official HTTP URLs.

**Tracked docs** (when promoting beyond the ticket):

1. Insert/merge rows into `RULE_SOURCE_URLS.md`
2. Update `COVERAGE_MATRIX.md` cells (normative URL? / gap)
3. Update the thematic companion (`ANNEX3_*` / `IWXXM_CREATION_*` / `IWXXM_VALIDATION_*`)
4. Add or refresh `*-mining-notes.md` for dense sources
5. Point from `docs/domain/rules/README.md` if a **new** notes file appears
6. Bump **Updated** date on edited catalogs

### 6. Hard rules

- **URLs + paraphrases only** in git — no Annex 3 / Doc 8896 / Manual on Codes full-text
- **No** `git add` of `.local/reference/` PDFs or `fulltext.txt`
- **No** edits inside `vendor/schemas/*` except via vendor sync PRs
- GIFTs = **historical gap baseline**, not ongoing SoT (ADR-014)
- Prefer `http://codes.wmo.int/...` concept URIs as written in schemas (https often works)
- Flag schema↔registry drift (404 concepts, casing mismatches) as **caveats**, do not invent URIs
- Commit **only** when the user asks

## Consumers map

| Finding type | Primary doc | Package consumer |
|--------------|-------------|------------------|
| TAC SARPs / FM templates | `validation/ANNEX3_TAC_VALIDATION_SOURCES.md` | `tac-validate` |
| nilReason / TAC→XML encoding | `iwxxm/IWXXM_CREATION_SOURCES.md` | `tac2iwxxm` |
| XSD / Schematron / codelist pins | `iwxxm/IWXXM_VALIDATION_SOURCES.md` | `iwxxm-validate` |
| All URL inventory | `rules/RULE_SOURCE_URLS.md` | design (#698/#699/#693) |
| Operator explanations | catalogs + notes | UI decode (#702), F7 (#714) |

## Done checklist

- [ ] Label + access recorded for each URL
- [ ] ≥1 actionable citation per in-scope product **or** explicit TBD/paywall row
- [ ] Gap vs GIFTs noted where relevant
- [ ] Vendor pin / namespace version cited when IWXXM schemas involved
- [ ] Companions cross-linked; no orphan mining notes
- [ ] Issue comments posted if requested; catalog updated if requested

## Additional resources

- Source class map: [source-classes.md](source-classes.md)
- Catalog row template: [catalog-row-template.md](catalog-row-template.md)
- Mining notes template: [notes-template.md](notes-template.md)
- Labeling glossary: `docs/domain/rules/README.md`
- Citation / paywall policy: `docs/domain/rules/ACCESS_AND_CITATION.md`
- PDF ingest: [extract-pdf-to-repo](../extract-pdf-to-repo/SKILL.md)
- Vocabulary: `.cursor/rules/core/iwxxm-domain-vocabulary.mdc`
