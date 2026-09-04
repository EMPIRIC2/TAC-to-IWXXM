---
name: mine-domain-sources
description: >
  Mines authoritative TAC validation, TAC→IWXXM conversion, and IWXXM validation
  sources into docs/domain/: lean canonicals (TAC_VALIDATION, IWXXM_CONVERSION,
  IWXXM_VALIDATION) + rules/ catalog, with dense digs under mining/ (transitory).
  Use when the user asks to mine a URL/repo/registry for domain rules, expand
  RULE_SOURCE_URLS, refresh canonical docs, or continue ticket-style discovery
  (e.g. #719) with issue comments and/or tracked notes.
---

# Mine domain sources → `docs/domain/`

Discovery / documentation skill for **rule provenance**. Produce citations, matrices, and
working notes — **not** engine rewrites, **not** copyrighted full-text dumps.

Complements [extract-pdf-to-repo](../extract-pdf-to-repo/SKILL.md) (PDF binary → `.local/` +
`mining/` notes). Use **this** skill for web/GitHub/registry/vendor mining and for
**promoting** durable findings into the standing canonicals.

When evolve needs a **deep-research agent handoff** first (scope → findings → promote
gates), start with [deep-research-domain-handoff](../deep-research-domain-handoff/SKILL.md)
(EV-097); return here for **gate C** promote / conflict resolution.

Hub: [`docs/domain/README.md`](../../../docs/domain/README.md). Domain is **not** minimal
corpus ([`docs/CORPUS.md`](../../../docs/CORPUS.md)).

## Lean layout (do not sprawl)

| Layer | What belongs | Path |
|-------|--------------|------|
| **Canonical (SoT for citations)** | Functional standing docs | `docs/domain/TAC_VALIDATION.md`, `IWXXM_CONVERSION.md`, `IWXXM_VALIDATION.md` |
| **Catalog** | URL inventory + coverage + citation policy | `docs/domain/rules/` |
| **Transitory digs** | Focused source digs; **not** SoT | `docs/domain/mining/<slug>-mining-notes.md` |
| **Ops / engineering (out of scope for this skill)** | Version UX, engine architecture | `docs/domain/iwxxm/`, `docs/domain/validation/` |

**Rule:** write dense passes under `mining/`; **promote** only durable URLs, matrices, and
encode/validate rules into the three canonicals + `rules/`. Do not treat mining notes as
equal weight to canonicals. Do not invent new standing docs under `domain/` without updating
`docs/domain/README.md`.

## When to use

- User provides a URL, WMO/ICAO landing, `codes.wmo.int` register, or `wmo-im/*` repo
- Expand or refresh canonicals / `rules/` catalog
- Ticket work that asks for mining comments (e.g. rule-source inventory)
- Map products (METAR…TCA) × (validation | conversion | iwxxm-validation)

## Destinations

| Output | Path | Standing? |
|--------|------|-----------|
| Domain hub | `docs/domain/README.md` | yes |
| TAC validation | `docs/domain/TAC_VALIDATION.md` | **canonical** |
| TAC→IWXXM conversion | `docs/domain/IWXXM_CONVERSION.md` | **canonical** |
| IWXXM XSD/SCH | `docs/domain/IWXXM_VALIDATION.md` | **canonical** |
| Master URL catalog | `docs/domain/rules/RULE_SOURCE_URLS.md` | catalog |
| Coverage matrix | `docs/domain/rules/COVERAGE_MATRIX.md` | catalog |
| Access / citation policy | `docs/domain/rules/ACCESS_AND_CITATION.md` | catalog (edit only if policy changes) |
| Focused working notes | `docs/domain/mining/<slug>-mining-notes.md` | **transitory** |
| Mining index | `docs/domain/mining/README.md` | list new notes here |
| Issue comments | Linked ticket | optional |

Prefer **vendor pins** as runtime truth: `vendor/manifest.json` (e.g. IWXXM **`v2025-2`**).
Prefer `https://schemas.wmo.int/iwxxm/<pin>/` over outdated printed package tables.

When mining reveals **contradictory claims**, follow [Conflict resolution](#conflict-resolution--defer-to-latest).

## Workflow

```
- [ ] 1. Scope — URL(s), products, role(s), ticket link
- [ ] 2. Classify source (see source-classes.md)
- [ ] 3. Mine — fetch / gh / vendor mirror; no full PDF scrape into git
- [ ] 4. Draft — mining notes (transitory) + catalog paste rows
- [ ] 4b. Conflict check — defer to latest; caveat older notes/canonicals
- [ ] 5. Publish — promote durable findings into canonicals + rules/; index mining/
- [ ] 6. Cross-link hub/canonicals (not every mining note from rules/README)
- [ ] 7. Commit only if user asks
```

### 1. Scope

| Field | Example |
|-------|---------|
| Source URL(s) | `https://github.com/wmo-im/iwxxm` |
| Products | F6: AIRMET · METAR · SIGMET · SPECI · TAF · VAA · TCA (+ SWX/VONA/WAFS if relevant) |
| Role | `validation` · `conversion` · `iwxxm-validation` · `bulletin` |
| Profile | `annex3` · `iwxxm_us` |
| Deliverable | issue comments · canonical update · mining notes · all |
| Ticket | `#719` etc. |

If the source is a **PDF**, hand off binary ingest to **extract-pdf-to-repo**, then continue
here for **canonical / catalog promotion**.

### 2. Classify

Read [source-classes.md](source-classes.md). Assign **label**:

`normative` | `normative-vocabulary` | `normative-schema` | `normative-conversion-notes` |
`normative-examples` | `normative-exchange` | `informative` | `historical-GIFTs`

Record **access**: public / register / captcha / **paywall**.

### 3. Mine

| Kind | How |
|------|-----|
| GitHub repo | `gh api` / clone; prefer **manifest SHA** / tag from `vendor/manifest.json`; use `vendor/schemas/*` when pinned |
| schemas.wmo.int | HTTP fetch of landing + examples; cite pin version |
| codes.wmo.int | Registers only; cite URIs — do not dump full registries into docs |
| Vendor tree | Read-only under `vendor/schemas/` |
| Paywalled ICAO/WMO PDF | Cite store/library landing + edition; local PDF → extract-pdf-to-repo → `.local/` |
| Community / translation fixtures | Mine, label **informative** |

Capture per finding: **publisher**, **stable URL**, **date mined**, **products**, **role**,
**gap vs GIFTs**, **consumer** (`tac-validate` \| `tac2iwxxm` \| `iwxxm-validate` \|
`UI-decode` \| `bulletin`).

### 4. Draft

- **Mining notes** (required for dense single-source passes) → `docs/domain/mining/`
  using [notes-template.md](notes-template.md). **Not SoT.**
- **Catalog row** → paste into `rules/RULE_SOURCE_URLS.md`
  ([catalog-row-template.md](catalog-row-template.md)).
- **Product matrix** (converter/schema sources):

| Product | TAC input artifact | IWXXM output (root / XSD) | Official example / guidance | Gap vs GIFTs | Consumer |

### 5. Publish

**Issue comments** (when ticket asks):

1. Overview (what source is / is not + landings)
2. Product × file or register matrix
3. Highlights + paste-ready catalog rows

**Tracked docs** (promote beyond the dig):

1. Write/refresh `mining/<slug>-mining-notes.md` (transitory)
2. Index it in `docs/domain/mining/README.md` if new
3. Merge durable rows into `rules/RULE_SOURCE_URLS.md`
4. Update `rules/COVERAGE_MATRIX.md` cells
5. Update the matching **canonical**:
   - TAC SARPs / FM templates / vocab → `TAC_VALIDATION.md`
   - nilReason / TAC→XML / examples → `IWXXM_CONVERSION.md`
   - XSD / Schematron / codelist pins → `IWXXM_VALIDATION.md`
6. Bump **Updated** on edited catalogs/canonicals
7. If superseding an older claim: caveat the older mining note **and** demote equal-weight
   SoT rows in canonicals/catalog (defer-to-latest)

Do **not** list every mining note in `rules/README.md` — that index stays canonical-only;
`mining/README.md` owns the dig list.

### Conflict resolution — defer to latest

When sources disagree on the **same claim**, **defer to the latest** and caveat the older.
Do not leave equal-weight conflicting SoT in canonicals or `RULE_SOURCE_URLS.md`.

**Order of preference:**

1. **Runtime / machine truth:** `vendor/manifest.json` pin + `schemas.wmo.int/iwxxm/<pin>/`
   (Schematron / examples / `TAC-to-XML-Guidance`) over printed tables or workshop decks.
2. **Same authority family:** later published/effective edition or tag beats older/unedited draft.
3. **Cross-document prose:** later official landing/edition; mark older **superseded** / historical.
4. **Label still matters:** newer **informative** never overrides older **normative** SARP/schema/
   registry. Quote as forward-looking until a later normative edition confirms it.
5. **GIFTs / historical:** never prefer GIFTs over later WMO/ICAO/vendor (ADR-014).

**Write-up:** mining notes get a **Domain-knowledge cross-check** table; canonicals/catalog keep
one **current** citation path.

### 6. Hard rules

- **URLs + paraphrases only** in git — no Annex 3 / Doc 8896 / Manual on Codes full-text
- **No** `git add` of `.local/reference/` PDFs or `fulltext.txt`
- **No** edits inside `vendor/schemas/*` except via vendor sync PRs
- **No** new standing `docs/domain/*.md` outside the hub table without updating `README.md`
- GIFTs = historical gap baseline only (ADR-014)
- Prefer `http://codes.wmo.int/...` concept URIs as written in schemas
- Flag schema↔registry drift as **caveats**; do not invent URIs
- **Contradictions → defer to latest**; never equal-weight conflicting SoT
- Commit **only** when the user asks

## Consumers map

| Finding type | Primary doc (canonical) | Package consumer |
|--------------|-------------------------|------------------|
| TAC SARPs / FM templates | `TAC_VALIDATION.md` | `tac-validate` |
| nilReason / TAC→XML encoding | `IWXXM_CONVERSION.md` | `tac2iwxxm` |
| XSD / Schematron / codelist pins | `IWXXM_VALIDATION.md` | `iwxxm-validate` |
| All URL inventory | `rules/RULE_SOURCE_URLS.md` | design (#698/#699/#693) |
| Operator explanations | canonicals + catalogs; digs in `mining/` | UI decode (#702), F7 (#714) |

## Done checklist

- [ ] Label + access recorded for each URL
- [ ] ≥1 actionable citation per in-scope product **or** explicit TBD/paywall row
- [ ] Gap vs GIFTs noted where relevant
- [ ] Vendor pin / namespace version cited when IWXXM schemas involved
- [ ] Durable findings in canonicals + `rules/`; dig only under `mining/` (+ README index)
- [ ] Contradictions resolved per defer-to-latest; older notes/canonicals caveated
- [ ] Issue comments posted if requested
- [ ] No sprawl into `iwxxm/` or `validation/` engineering trees unless user asked for ops notes

## Additional resources

- Domain hub: `docs/domain/README.md`
- Source class map: [source-classes.md](source-classes.md)
- Catalog row template: [catalog-row-template.md](catalog-row-template.md)
- Mining notes template: [notes-template.md](notes-template.md)
- Labeling glossary: `docs/domain/rules/README.md`
- Citation / paywall policy: `docs/domain/rules/ACCESS_AND_CITATION.md`
- PDF ingest: [extract-pdf-to-repo](../extract-pdf-to-repo/SKILL.md)
- Vocabulary: `.cursor/rules/core/iwxxm-domain-vocabulary.mdc`
