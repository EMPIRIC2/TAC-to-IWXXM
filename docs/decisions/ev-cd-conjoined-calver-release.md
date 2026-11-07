# Decisions — EV-cd-conjoined-calver-release

**Date:** 2026-11-07  
**Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-cd-conjoined-calver-release`  
**Corpus:** [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: adr/ADR-043] [Corpus: product §F12–F14] [Corpus: product §F30] [Corpus: tests]

## Summary

Rework Continuous Delivery so DOKS, GHCR, and PyPI/TestPyPI ship under one CalVer.
Create one GitHub Release for each production ship. Remove soft-fail nightlies and
`v*-deploy` tags.

## Decisions

| ID | Decision |
|----|----------|
| Q1 | Merges to `main` start prod CD (DOKS + GHCR + PyPI + Release) |
| Q2 | No daily cron; ships run when branches receive merges |
| Q3 / R1 | TestPyPI versions = `{CalVer}+test` (PEP 440 local) |
| Q4 | One GitHub Release per ship (`vYYYY.M.D[.N]`) |
| Q5 | Drop `v*-deploy` tags; keep `workflow_dispatch` for manual redeploy only |
| R2 | Same-day re-ship auto-bumps `YYYY.M.D.N` |
| R3 | Docs/infra-only: DOKS + GHCR + Release; skip PyPI |
| R4 | CD creates `{pkg}-v*` tags → existing `pypi-publish.yml` |
| ADR | Amend ADR-043 Part B and ADR-034 (no new ADR id) |

## Replaces

- EV-051 rule that `main` is CI only and prod needs `v*-deploy`
- ADR-043 alternative that blocked auto-publish on every `main` push
- Scheduled `pypi-nightly.yml` / `.devN` TestPyPI path

## Follow-on (Build)

Change workflows and scripts. Set up Trusted Publisher / TestPyPI. Map Cargo for
`+test`. Delete or disable `pypi-nightly.yml`.
