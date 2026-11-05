# Wiki link map

Cross-page links in `user-docs/docs/` must target the **GitHub Wiki**, not
relative MkDocs paths.

**Wiki base:** `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki`

| Source file | Wiki page URL |
|-------------|---------------|
| `docs/index.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Home` |
| `docs/getting-started.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Getting-started` |
| `docs/examples/index.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Examples` |
| `docs/api/index.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API` |
| `docs/api/first-convert-call.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-First-convert-call` |
| `docs/api/authentication.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-Authentication` |
| `docs/api/example.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-Example` |
| `docs/web-app/index.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app` |
| `docs/web-app/convert-and-validate.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app-Convert-and-validate` |
| `docs/web-app/work-history.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app-Work-history` |
| `docs/web-app/example.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app-Example` |
| `docs/python-packages/index.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Python-packages` |
| `docs/python-packages/example.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Python-packages-Example` |
| `docs/python-packages/tac2iwxxm.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac2iwxxm` |
| `docs/python-packages/tac-validate.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac-validate` |
| `docs/python-packages/iwxxm-validate.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-iwxxm-validate` |
| `docs/python-packages/tac-decoding.md` | `https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac-decoding` |

## Rules

1. Editable cross-page links use the Wiki URLs in the table.
2. External hosts (PyPI, app, API, OpenAPI) stay on their own hosts.
3. When you publish to `.wiki.git`, name Wiki files to match the Wiki page
   titles in the table (for example `HTTP-API.md`, `Home.md`).
4. MkDocs local preview may leave the local site when you follow a Wiki link.
   That behavior is intended.

## Check

```bash
python3 user-docs/scripts/check_wiki_links.py
```
