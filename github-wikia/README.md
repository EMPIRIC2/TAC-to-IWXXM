# Public guide sources (MkDocs / Read the Docs)

This directory holds operator and integrator guides for TAC to IWXXM.
MkDocs builds the pages. You can also publish the same Markdown to the GitHub Wiki.

| Item | Value |
|------|-------|
| Theme | MkDocs built-in `readthedocs` |
| Cross-page links | Absolute GitHub Wiki URLs (`wiki-link-map.md`) |
| Language | ASD-STE100 Issue 9 for editable prose |
| Config | `mkdocs.yml`, repo-root `.readthedocs.yaml` |
| Wiki sidebar | `wiki/_Sidebar.md` (publish into `.wiki.git`) |

## Build locally

```bash
pip install -r requirements.txt
mkdocs serve
```

Open the local URL that MkDocs prints (often `http://127.0.0.1:8000`).

## Link rule

Cross-page navigation must point at the Wiki itself:

`https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/<Page-title>`

See [wiki-link-map.md](wiki-link-map.md). Check with:

```bash
python3 github-wikia/scripts/check_wiki_links.py
```

## Publish to GitHub Wiki

1. Clone `https://github.com/EMPIRIC2/TAC-to-IWXXM.wiki.git` (created on first push).
2. Copy each `docs/*.md` page to the Wiki page title in `wiki-link-map.md`
   (for example `docs/api/index.md` → `HTTP-API.md`).
3. Copy `wiki/_Sidebar.md` to the Wiki repo root as `_Sidebar.md`.
4. Commit and push the Wiki repo.

## Optional Read the Docs mirror

Follow [READTHEDOCS.md](READTHEDOCS.md). No public `tac-to-iwxxm` RTD project
existed when this guide was added. Keep Wiki URLs in page bodies so navigation
still lands on the Wiki.

## Publish helpers

```bash
python3 github-wikia/scripts/check_wiki_links.py
python3 github-wikia/scripts/publish_wiki.py --wiki-dir /tmp/TAC-to-IWXXM.wiki
```

## STE note

No tool guarantees ASD-STE100 compliance. A human must review Issue 9 against
editable prose. Protected regions (fenced code, URLs, TAC or XML samples) stay as
written.
