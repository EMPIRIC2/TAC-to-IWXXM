# Link the Read the Docs project

No Read the Docs project named `tac-to-iwxxm` exists yet (public API returned
zero results on 2026-11-05). Cross-page links in the Markdown still point at
the GitHub Wiki. Read the Docs is an optional mirror that uses the same
MkDocs sources.

## Create and link (operator)

1. Sign in at https://app.readthedocs.org/
2. Select **Import a Project**.
3. Choose GitHub repository `EMPIRIC2/TAC-to-IWXXM`.
4. Make sure that the project reads the repo-root file `.readthedocs.yaml`.
5. Trigger a build.
6. Copy the assigned docs URL (for example `https://<slug>.readthedocs.io/`).
7. Set that URL as `site_url` in `github-wikia/mkdocs.yml`.
8. Do not invent a host name before Read the Docs assigns one.

## Repo files already prepared

| File | Role |
|------|------|
| `.readthedocs.yaml` | RTD build: Python 3.12 + MkDocs config |
| `github-wikia/mkdocs.yml` | Nav and `readthedocs` theme |
| `github-wikia/requirements.txt` | `mkdocs>=1.6,<2` |

## Local build (same as RTD)

```bash
uvx --from 'mkdocs>=1.6,<2' mkdocs build --config-file github-wikia/mkdocs.yml --strict
```

## After the project exists

Tell the maintainers the live `site_url`. Then a follow-up commit can set
`site_url` in `mkdocs.yml` and add the URL to `docs/README.md`.
