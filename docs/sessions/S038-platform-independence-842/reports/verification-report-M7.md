# Verification report — M7 H4–H5 / live verify / close — EV-031 / S038

> **Date**: 2026-08-03  
> **Branch tip**: `f1e2389d`  
> **Scope**: T7.1–T7.4 (T6.5 remains M6 soak-blocked)

## Task results

| Task | Result | Evidence |
|------|--------|----------|
| T7.1 Playwright F31 live | **PASS** 13/13 | [t7.1-playwright-live-provisional.md](t7.1-playwright-live-provisional.md) |
| T7.2 H4–H5 DOKS | **PASS** H0c 6/6, H4 2/2, H5 | [t7.2-h4-h5-connectivity-provisional.md](t7.2-h4-h5-connectivity-provisional.md) |
| T7.3 TC-F30-006 / TC-EV031 | **PASS** unit 31 + live 3/3 | [t7.3-tc-ev031-topology.md](t7.3-tc-ev031-topology.md) |
| T7.4 Docs stubs + CORPUS note | **PASS** | evolve-summary, deploy-report, corpus-parity-note, CHANGELOG Unreleased |

## Connectivity artifacts

| Artifact | Present |
|----------|---------|
| `make test-live-connectivity-doks-provisional` | yes |
| `make test-live-e2e-doks-provisional` | yes |
| `make test-live-topology-doks-provisional` | yes |
| `scripts/deploy/verify_connectivity.sh` Host-aware | yes |

## Gate notes

- Provisional HTTP Host-header path satisfies H4–H5 under `D-S038-t63-waive`.
- HTTPS + real DNS and Render decommission remain **T6.5** / waive lift.
- **08-verify-build** full suite not re-run this boundary; live + unit evidence above is the M7 acceptance pack.

## Handoff

- Next unblocked work: none until soak calendar unlocks **T6.5**, or ops GHCR `write:packages` republish residual.
- Evolve PR → `main` after T6.5 + Phase D close (execution-plan PR Plan).
