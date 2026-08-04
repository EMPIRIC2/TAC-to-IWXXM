# QA Report — S040 / EV-032 (T4.3 / 09-qa delta)

> Generated: 2026-08-04  
> Scope: Delta QA for F32 VONA + EV-032 deepen (#835/#808/#846) — UJ-045  
> Branch: `evolve/EV-032-iwxxm-corpus-quality` @ `7b3c329b` (+ T4.3 report commit)  
> Mode: evolve delta (not full-repo remediating QA)  
> Prior 08: T4.2 **PASS** (`verification-report.md`)

## Summary

| Check | Status | Notes |
|-------|--------|-------|
| Format / lint / typecheck / secrets | PASS | `make validate-fast` |
| VONA quality pack | PASS | `make test-vona-quality` |
| EV-032 canaries (A6-2 + VONA) | PASS | 3 + 4 |
| TC-F32 lint/encode/golden | PASS | 16 pytest (001–004 paths) |
| TC SIGMET deepen (#835 path) | PASS | `make test-tc-sigmet-quality` |
| FE Vitest (UJ-045 surface) | PASS | 44 — catalog + tacProduct + product pickers (incl. VONA) |
| H0c CORS | PASS | 6 |
| H0i integration | PASS (local) | 6 passed / 9 skipped (Docker/live not required for delta) |
| H4–H5 staging browser | ADVISORY → T4.5 | Required at 13-deploy-smoke (E32-T6; FE VONA shipped) |
| pip-audit | SKIPPED | not in uv env; gitleaks + frontend audit via validate-ci (T4.2) |

**Overall: pass_with_advisories** (H4–H5 deferred to T4.5 / 13)

## Feature / journey coverage (delta)

| Item | Status |
|------|--------|
| F32 VONA lint → convert → XSD+SCH | PASS — vona-quality + TC-F32 |
| F7 picker + Examples unlock | PASS — Vitest product list + `vona_a7_1` wmoPass |
| #835 A6-2-TC ADR-032 / catalog | PASS — canary + tc-sigmet-quality |
| #808 / #847 docs | PASS — docs-only (prior M3); no QA code path |
| UJ-045 T0 | PASS — see e2e-report.md |

## Advisories

1. **H4–H5** — live browser connectivity for VONA FE deferred to **T4.5 / 13-deploy-smoke** (`scripts/deploy/verify_connectivity.sh`; needs `LIVE_API_URL` + `LIVE_FRONTEND_URL`)
2. Integration live skips — expected without Docker Compose stack in this delta run
3. No dedicated Playwright VONA journey yet — T0 covered by Vitest + API smoke; T2/T3 browser proof at deploy

## Blocking findings

None.

## H4–H5 prep checklist (for T4.5)

- [x] FE product picker includes **VONA**
- [x] Examples catalog unlocks `vona-A7-1` as `wmoPass`
- [x] API runtime `product=vona` (TC-F32-005/006)
- [x] `scripts/deploy/verify_connectivity.sh` present
- [ ] Redeploy API + static (T4.5)
- [ ] Run H1–H3 + H4–H5 against live URLs (T4.5 / TC-EV032-007/008)
