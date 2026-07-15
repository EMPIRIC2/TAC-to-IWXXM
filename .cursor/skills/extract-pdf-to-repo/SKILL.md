---
name: extract-pdf-to-repo
description: >
  Download or copy a PDF into the repo, extract page-marked text under .local/
  (gitignored), and write focused mining notes under docs/domain/mining/ (transitory).
  Promote durable citations into TAC_VALIDATION / IWXXM_CONVERSION / IWXXM_VALIDATION
  via mine-domain-sources. Use when the user provides a PDF path/URL, asks to extract
  or mine a PDF, or wants LLM-readable reference text saved locally (WMO manuals,
  standards, specs).
---

# Extract PDF to repo

Ingest a PDF for LLM mining: **binary + full extract stay gitignored**; **focused digs
are tracked under `docs/domain/mining/`** (transitory — **not** SoT).

Complements [mine-domain-sources](../mine-domain-sources/SKILL.md): this skill owns PDF
→ `.local/` + `mining/` notes; mine-domain-sources owns **promotion** into lean canonicals
and `rules/`. Hub: [`docs/domain/README.md`](../../../docs/domain/README.md).

## Lean domain layout

| Layer | Path | This skill writes? |
|-------|------|--------------------|
| Local binary + extracts | `.local/reference/<slug>/` | **yes** (gitignored) |
| Transitory digs | `docs/domain/mining/<slug>-mining-notes.md` | **yes** (tracked notes) |
| Canonical SoT | `TAC_VALIDATION.md` · `IWXXM_CONVERSION.md` · `IWXXM_VALIDATION.md` | **promote only** (hand off or continue with mine-domain-sources) |
| Catalog | `docs/domain/rules/` | promote durable URL rows only |
| Ops / engine trees | `docs/domain/iwxxm/`, `validation/` | **no** (unless user explicitly asks) |

Do **not** invent new standing `docs/domain/*.md` files. Do **not** treat mining notes as
equal to canonicals. Do **not** invent `[Corpus]` members (`domain/` is not minimal corpus).

## Layout

```
.local/reference/<slug>/          # gitignored (.local/)
  README.md                       # source URL, edition, provenance → notes path
  <original-filename>.pdf
  fulltext.txt                    # ===== PAGE N ===== markers
  pages.jsonl                     # {"page": N, "text": "..."} per line
  extracts/                       # optional topic dumps

docs/domain/mining/<slug>-mining-notes.md   # tracked dig (transitory)
```

`<slug>`: kebab-case id, e.g. `wmo-306-vI-3-2023`.

## Destinations

| Content type | Path |
|---|---|
| Domain mining digs (**transitory**) | `docs/domain/mining/<slug>-mining-notes.md` |
| Index new dig | `docs/domain/mining/README.md` |
| Promote durable findings | `docs/domain/TAC_VALIDATION.md`, `IWXXM_CONVERSION.md`, `IWXXM_VALIDATION.md` + `rules/RULE_SOURCE_URLS.md` / `COVERAGE_MATRIX.md` |
| Session-only scratch | `docs/sessions/<id>/` (only if an active session owns it) |

Prefer official schemas/HTML over OCR’d PDF when normative conversion recipes matter.

## Workflow

```
- [ ] 1. Resolve source (path / URL / user upload)
- [ ] 2. Confirm slug; notes path = docs/domain/mining/<slug>-mining-notes.md
- [ ] 3. Store PDF under .local/reference/<slug>/
- [ ] 4. Run extract script → fulltext.txt + pages.jsonl
- [ ] 5. Ask focus (section / topic) — do not "mine everything"
- [ ] 6. Carve extracts/ + write mining notes (transitory)
- [ ] 7. Index in docs/domain/mining/README.md if new
- [ ] 8. Promote durable citations (canonicals + rules/) — or invoke mine-domain-sources
- [ ] 9. Commit only if user asks (tracked notes only — never .local/)
```

### 1. Resolve source

| Source | Action |
|---|---|
| Local path in workspace | Copy into `.local/reference/<slug>/` |
| `file://` or host path outside workspace | Ask user to upload/copy into the workspace |
| HTTP(S) URL | `curl -L` with a normal User-Agent; verify `file` is PDF |
| Captcha / HTML interstitial (e.g. WMO e-Library) | Try Wayback `…/web/<ts>if_/…`; else ask user to upload |

Reject HTML stubs: if `file` is not `PDF document`, delete and escalate.

### 2. Extract

Prefer the skill script (pypdf):

```bash
python3 .cursor/skills/extract-pdf-to-repo/scripts/extract_pdf.py \
  .local/reference/<slug>/<file>.pdf
```

Writes sibling `fulltext.txt` and `pages.jsonl`. Large PDFs may take 1–2 minutes — await completion.

Fallback: `pdftotext -layout` if installed; still produce page markers when possible.

### 3. Focused mining (required)

Before summarizing, confirm focus with the user (or use an explicitly stated focus). Prefer:

- Named sections / FM codes / requirement classes
- Code tables / nil-missing vocabularies
- Version-specific schema pointers

Write **tracked digs** under `docs/domain/mining/` as working notes (**not normative**). Always cite:

- Official permalink / store-library landing
- Local `.local/reference/<slug>/` paths
- PDF page numbers from `fulltext.txt` markers

Templates:

- Domain digs: [mine-domain-sources/notes-template.md](../mine-domain-sources/notes-template.md)
- PDF-oriented fields: [notes-template.md](notes-template.md)

When the PDF maps to TAC / conversion / IWXXM roles, prefer the mine-domain-sources
template (product matrix, catalog paste rows, defer-to-latest cross-check).

### 4. Provenance README

In `.local/reference/<slug>/README.md` record: title, edition/year, official URL, how the
PDF was obtained, and pointer to **`docs/domain/mining/<slug>-mining-notes.md`**.

### 5. Promote (required for binding claims)

Mining notes alone are **not** standing SoT. After the dig:

1. Paste durable catalog rows into `docs/domain/rules/RULE_SOURCE_URLS.md`
2. Update `COVERAGE_MATRIX.md` if product coverage changed
3. Update the matching canonical:
   - TAC SARPs / FM / vocab → `TAC_VALIDATION.md`
   - Encode / nilReason / examples → `IWXXM_CONVERSION.md`
   - XSD / Schematron / pins → `IWXXM_VALIDATION.md`
4. Conflict → **defer to latest** per mine-domain-sources; caveat older digs/canonicals

If the pass is dig-only (user said “notes only”), stop after step 3 of workflow and say
promotion is pending.

## Rules

- **Binary + fulltext = `.local/` only** (gitignored). Never `git add` PDFs or raw extracts.
- **Tracked digs = `docs/domain/mining/` only** for domain PDFs — not `iwxxm/` or ad-hoc roots.
- **No commit** unless the user asks; then commit only tracked notes / skill / link fixes — not `.local/`.
- Normalize broken PDF URL spaces (`codes .wmo .int` → `codes.wmo.int`) in notes.
- Paywalled PDFs: cite landings + pages; never redistribute copyrighted full text in git.
- Cross-link: hub + canonical when promoting; digs index in `mining/README.md`.

## Done checklist

- [ ] PDF + `fulltext.txt` / `pages.jsonl` under `.local/reference/<slug>/`
- [ ] Provenance README points at mining notes path
- [ ] Focused dig at `docs/domain/mining/<slug>-mining-notes.md`
- [ ] New dig listed in `docs/domain/mining/README.md`
- [ ] Durable findings promoted to canonicals + `rules/` **or** explicitly deferred
- [ ] No full-text / PDF staged for commit

## Additional resources

- Domain hub: `docs/domain/README.md`
- Promotion / conflict rules: [mine-domain-sources](../mine-domain-sources/SKILL.md)
- PDF notes template: [notes-template.md](notes-template.md)
- Domain dig template: [mine-domain-sources/notes-template.md](../mine-domain-sources/notes-template.md)
- Extract script: [scripts/extract_pdf.py](scripts/extract_pdf.py)
- Example dig: `docs/domain/mining/WMO-306-vI-3-2023-mining-notes.md`
- Citation policy: `docs/domain/rules/ACCESS_AND_CITATION.md`
