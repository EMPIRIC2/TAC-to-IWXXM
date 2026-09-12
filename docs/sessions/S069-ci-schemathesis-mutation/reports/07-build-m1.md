# 07-build — S069 / EV-059 M1 Schemathesis (#727)

> **Status**: M1 complete pending merge  
> **Date**: 2026-08-17  
> **Decisions**: `D-S069-07-start=1a..6a`  
> **Corpus**: [Corpus: product §F34] [Corpus: tests] [Corpus: tech-spec] [Corpus: api]

## Delivered

| Task | Result |
|------|--------|
| T1.1 | `schemathesis==4.24.3` in workspace `dev` + inventory pin |
| T1.2 | `apps/backend/tests/contract/test_schemathesis_openapi.py` ASGI + auth override |
| T1.3 | `make test-schemathesis` (`SCHEMATHESIS_MAX_EXAMPLES` ≤ 25) |
| T1.4 | `.github/workflows/schemathesis.yml` path filter + **Schemathesis gate** (≤10 min) |
| T1.5 | Allow documented 501 on ingest-collect; exclude work-sessions/eval/auth |
| T1.6 | PR [#997](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/997) → `stage`; CI green |

## CI

- Schemathesis: https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32044906406 — **success**
- CI/CD: https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32044906428 — **success**

## Next

1. User merge approval for #997  
2. M2 mutation (#874) on same evolve branch after merge (do not bundle with #727)
