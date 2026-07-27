# Context — rename cutover (#781)

**Session:** S022-rename-cutover (proposed)  
**Date:** 2026-07-27  
**Corpus:** `[Corpus: tech-spec]` (`docs/deploy.md`, deploy-state) — not product Fn

## Why now

S021 / EV-016 merged F7.g (PR #782 @ `c49f22b`) and pushed Empiric2 GHCR images, but Render
still pulls `ghcr.io/joseph-c-mcguire/metar-to-iwxxm/*`. Deploy hook returned **400**; live FE
has no Examples/goldens UI. Live H4–H5 was waived to this ticket.

## Current live vs target

| Layer | Current | Target |
|-------|---------|--------|
| GitHub repo | `EMPIRIC2/TAC-to-IWXXM` | (done) |
| CI image names | `ghcr.io/empiric2/tac-to-iwxxm/*` | (done; packages pushed for `c49f22b`) |
| Render API/FE imagePath | `ghcr.io/joseph-c-mcguire/metar-to-iwxxm/{backend,frontend}:main-latest` | `ghcr.io/empiric2/tac-to-iwxxm/{backend,frontend}:main-latest` |
| Worker repo | `joseph-c-mcguire/metar-to-IWXXM` | `EMPIRIC2/TAC-to-IWXXM` |
| Live URLs | Keep `metar-to-iwxxm-*.onrender.com` | No hostname rename in this ticket |
| Commit live | `eae8bdc…` (pre–#782) | `c49f22b` or later `main` |

## Live URLs (unchanged hostnames)

- API: https://metar-to-iwxxm-api.onrender.com
- Frontend: https://metar-to-iwxxm-frontend-v4-web.onrender.com

## Risks / admin gates

- Org admin may be required for GHCR visibility and PyPI Trusted Publisher
- Render workspace must be selected before MCP/CLI mutations
- Do not rename onrender hostnames without CORS + config/prod.json plan

## Downstream backlog (after this session)

- #731 AIRMET → SIGMET/advisory quality chain
- #777 publish `iwxxm-dissemination`
