# Deploy Checklist — S046 / EV-038 (Stage 12 / T5.4)

> Generated: 2026-08-06  
> Status: **APPROVED** (`D-S046-12`=1) — open PR → merge → 13  
> Prior: 11 **APPROVED** (`D-S046-11`=1)  
> Deployment: [docs/deploy.md](../../../deploy.md) · DOKS CD on `main`  
> Branch: `evolve/EV-038-iwxxm-corpus-residuals` @ `2195978e` (+ T5.3 commit)  
> Lock: **S02.M5** — API + static redeploy; H1–H3; **H4–H5 required** (UJ-050 / #854)  
> Corpus: `[Corpus: tech-spec]` · `[Corpus: tests]` · connectivity-gates §12–13

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `apps/backend` + `iwxxm_versions.py` | SoT versions / OpenAPI enum | **Redeploy API** |
| `apps/frontend` | Latest/Previous picker (#854); catalog VA-EGGX `wmoPass` | **Rebuild static FE** |
| `packages/tac2iwxxm` | VONA vertical extent; VA-EGGX equality | In API image — **redeploy API** |
| Docs / process | M1–M3 residuals | No runtime alone |
| Auth/CORS | Unchanged origins | Re-verify H4–H5 post-deploy |
| Worker / dissemination | Unchanged | No worker redeploy required |
| Secrets / DB | None new | N/A |

**Pre-merge:** Staging/prod tracks `main` tip `d3f4bb95` (drift vs EV-038). Land via PR merge → DOKS CD (same path as EV-034 / S042).

## Pre-Deploy

- [x] Configuration complete — DOKS + GHCR image CD; no new services
- [x] Secrets — no new keys
- [x] Data assets — vendor schemas in image
- [x] Resource allocation — unchanged
- [x] Rollback — prior DOKS/GHCR tag / previous rollout
- [x] H0c CORS — 6/6 (T5.1 / T5.2)
- [x] Connectivity scripts — `scripts/deploy/verify_connectivity.sh`
- [x] Local `make ci` green on branch push
- [ ] PR to `main` opened
- [ ] Merge approved + CD SUCCESS
- [ ] Post-deploy H1–H3 + **H4–H5**

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image/CD failure | `ci-cd.yml` on PR + Deploy job | pending PR |
| 2 | VA-EGGX / VONA regression | `test-va-sigmet-quality` + `test-vona-quality` @ 08 | **ready** |
| 3 | FE missing Latest/Previous | Vitest + Playwright UJ-050; **H4–H5 required** | **ready** |
| 4 | CORS after FE rebuild | `verify_connectivity.sh` | **ready** |
| 5 | Deploy drift (main ≠ branch) | Merge before smoke | pending |

## Rollback

- Roll back DOKS deployments to prior GHCR tag (`20260805115809-d3f4bb9` or last green)
- Re-run `make test-live-connectivity`
- No DB migrations this cycle

## Redeploy order (T5.4 / 13)

1. Open PR `evolve/EV-038-iwxxm-corpus-residuals` → `main`; wait CI green.
2. **Merge** (explicit user approval).
3. Wait DOKS CD (API + frontend images).
4. H0c (already green) → H1–H3 → **`bash scripts/deploy/verify_connectivity.sh`** (H4–H5).
5. Optional: Playwright UJ-050 against `LIVE_FRONTEND_URL`.

## Recommended D-S046-12

Approve checklist as written; open PR next; merge + 13 smokes after CI green.
