# Decision — Public user docs on Read the Docs (MkDocs)

**Session:** EV-github-wiki-docs  
**Date:** 2026-11-05  
**Status:** accepted (operator: proceed with recommendations + Read the Docs format)

## Context

The evolve goal was public documentation for the HTTP API, the web app, and the
Python packages, written to ASD-STE100 Issue 9. The first intake named GitHub
Wiki. The operator then required the same format as Read the Docs sites
(sidebar navigation, Getting Started, hierarchical guides).

## Decision

1. **Authoring format:** MkDocs with the built-in `readthedocs` theme under
   `user-docs/` (sidebar layout like Read the Docs). Optional RTD build via
   `.readthedocs.yaml`.
2. **Link target:** Cross-page links in user docs must use absolute
   **GitHub Wiki** URLs under
   `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/…` (see
   `user-docs/wiki-link-map.md`). Do not use relative `.md` paths for page
   navigation. External hosts (PyPI, app, API) stay on their own hosts.
3. **Language:** ASD-STE100 Issue 9 for editable prose. Dictionary:
   `docs/ste/ASD-STE100_ISSUE9.txt`. Protected regions (code, URLs, TAC/XML
   samples, product names) stay unchanged.
4. **Not a design gate:** Engineering truth stays in CORPUS rows `api`,
   `product`, `system-spec`, and live OpenAPI. The user site summarizes for
   operators and integrators.
5. **Publish:** Push renamed pages + `user-docs/wiki/_Sidebar.md` to
   `TAC-to-IWXXM.wiki.git` using the link map titles. Empty Wiki bootstrap
   happens on first page push.
6. **Dependency:** `mkdocs` `>=1.6,<2` in `user-docs/requirements.txt` and the
   dependency inventory. Dev-only docs tool.

## Consequences

- Public readers use the GitHub Wiki for navigation (absolute Wiki URLs).
- MkDocs + optional Read the Docs mirror the same sources (RTD project must be
  created at app.readthedocs.org — none existed for slug `tac-to-iwxxm` on
  2026-11-05; see `user-docs/READTHEDOCS.md`).
- Agents cite `[Corpus: user-docs]` only for narrative user guidance, never as
  a substitute for `[Corpus: api]` on HTTP contract changes.
