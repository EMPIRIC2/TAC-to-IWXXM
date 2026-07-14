---
name: extract-pdf-to-repo
description: >
  Download or copy a PDF into the repo, extract page-marked text, and write focused
  mining notes under docs/. Use when the user provides a PDF path/URL, asks to extract
  or mine a PDF, or wants LLM-readable reference text saved locally (WMO manuals,
  standards, specs).
---

# Extract PDF to repo

Ingest a PDF for LLM mining: **binary + full extract stay gitignored**; **focused notes are tracked**.

## Layout

```
.local/reference/<slug>/          # gitignored (.local/)
  README.md                       # source URL, edition, provenance
  <original-filename>.pdf
  fulltext.txt                    # ===== PAGE N ===== markers
  pages.jsonl                     # {"page": N, "text": "..."} per line
  extracts/                       # optional topic dumps

docs/<area>/...-mining-notes.md   # tracked summary (see Destinations)
```

`<slug>`: kebab-case id, e.g. `wmo-306-vI-3-2023`.

## Destinations (tracked notes)

| Content type | Path |
|---|---|
| IWXXM / METAR / codes domain | `docs/domain/iwxxm/` |
| Other domain deep-dives | `docs/domain/<topic>/` |
| Session-only scratch | `docs/sessions/<id>/` (only if an active session owns it) |

Do **not** invent new top-level corpus members. Do **not** commit PDFs or `fulltext.txt`.

## Workflow

Copy this checklist:

```
- [ ] 1. Resolve source (path / URL / user upload)
- [ ] 2. Confirm slug + notes destination with user if ambiguous
- [ ] 3. Store PDF under .local/reference/<slug>/
- [ ] 4. Run extract script → fulltext.txt + pages.jsonl
- [ ] 5. Ask focus (section / topic) — do not "mine everything"
- [ ] 6. Carve extracts/ + write tracked mining notes
- [ ] 7. Link notes from an existing domain doc if one already cites the source
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

Write **tracked notes** as working notes (not normative). Always cite:

- Official permalink
- Local `.local/reference/<slug>/` paths
- PDF page numbers from `fulltext.txt` markers

Template: see [notes-template.md](notes-template.md).

### 4. Provenance README

In `.local/reference/<slug>/README.md` record: title, edition/year, official URL, how the PDF was obtained, and pointer to the tracked notes path.

## Rules

- **Binary + fulltext = `.local/` only** (already gitignored). Never `git add` PDFs or raw extracts.
- **No commit** unless the user asks; then commit only tracked notes / skill / link fixes — not `.local/`.
- Prefer official schemas/HTML over OCR’d PDF when normative conversion recipes matter.
- Normalize broken PDF URL spaces (`codes .wmo .int` → `codes.wmo.int`) in notes.
- If extract is for an approved corpus topic, place notes beside existing domain docs and cross-link once.

## Additional resources

- Notes template: [notes-template.md](notes-template.md)
- Extract script: [scripts/extract_pdf.py](scripts/extract_pdf.py)
- Example output: `docs/domain/iwxxm/WMO-306-vI-3-2023-mining-notes.md`
