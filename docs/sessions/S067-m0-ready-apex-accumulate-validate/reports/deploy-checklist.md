# Deploy Checklist — S067 / EV-057 (12-verify-deploy)

> Generated: 2026-08-16  
> Status: **APPROVED** (`D-S067-12-scope=1a` / `D-S067-12-risks=1a` / `D-S067-12-merge=1a`) — 12 COMPLETE; Staging CD green  
> Prior: 11 **APPROVED** (`D-S067-11-ac=1a`); resume `D-S067-12-resume=1a`  
> Deployment: [docs/deploy.md](../../../deploy.md) · dual DOKS (ADR-034)  
> Tip: `d05c23b7` · PR [#991](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/991) → `stage`  
> Tip CI: [CI/CD Pipeline 31965556483](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31965556483) **success** @ `d05c23b7`  
>   (prior fail [31964710714](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31964710714) @ `a730d7a3` — Vitest branch coverage; fixed on tip)  
> `env_role`: **staging** first (PR → `stage` → cluster `metar-iwxxm-staging`); promote held (`D-S067-promote=2b`)  
> Corpus: [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: product §F7] [Corpus: product §F30] [Corpus: tests]

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `deploy/doks` | Apex/www redirect (#948); staging short-host YAML | Prod apex **already live**; staging short-host apply only if DNS ready |
| `apps/frontend` | Accumulate ZIP (#903); Validate IWXXM mode (#838) | FE rebuild / static deploy on `stage` |
| `apps/e2e` | UJ-057 / UJ-058 specs | CI / staging smoke; live H4–H5 in **13** |
| Env / secrets | No new secrets | Confirm staging CORS includes `https://app.staging.tac-to-iwxxm.com` |
| Worker / DB migrations | None | N/A |

**Path:** Merge #991 → `stage` → Staging Deploy + Staging smoke → **13** H4–H5. Do **not** open feature→`main`. Promote only after separate re-approve.

## Pre-Deploy

- [x] Configuration — no new env knobs for #903/#838; #948 Ingress already applied on prod
- [x] Secrets — none new
- [x] Data assets — N/A
- [x] Resource allocation — unchanged
- [x] Rollback — prior GHCR/`stage-latest` on staging DOKS
- [x] H0c CORS — `tests/unit/test_cors_policy.py` present (PASS in 08/09)
- [x] Connectivity scripts — `scripts/deploy/verify_connectivity.sh` + `tests/smoke/test_staging_connectivity.py` present
- [x] Branch pushed — tip `d05c23b7`
- [x] Tip CI green — [31965556483](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31965556483) @ `d05c23b7`
- [x] PR open — [#991](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/991) MERGEABLE
- [x] Merge + Staging CD — **MERGED** #991 @ `d7022f1f`; Deploy+Staging smoke [31966102210](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31966102210) **success**
- [ ] Post-deploy H1 + **H4–H5** (13) — UJ-057/058 after Staging smoke

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image/CD failure on stage | Tip CI green on PR #991 before merge | **approved** (`D-S067-12-risks=1a`) |
| 2 | Staging CORS / XHR miss for #903/#838 | Existing CORS matrix; H4–H5 at 13 | **approved** / verify at 13 |
| 3 | Accidental promote to main | Dual-env: stage smoke + Staging gate; `D-S067-promote=2b` | **approved** |
| 4 | Staging short-host / apex YAML applied without DNS | Apply only if A → `143.244.202.13`; #948 prod already live | **approved** |

## Rollback

- Roll back staging DOKS deployments to prior GHCR tag / `stage-latest` predecessor
- Re-run `bash scripts/deploy/verify_connectivity.sh` with staging URLs
- No DB migrations this cycle
- Prod apex redirect (#948) is already live — rollback of that path is separate from this stage merge

**Approved** (`D-S067-12-merge=1a`).

## Recommended path (13)

1. Tip CI green on `d05c23b7` / PR #991 — **done**.
2. User approve this checklist (12) — **`D-S067-12-*` recommended path**.
3. **Merge** #991 → `stage` → Staging Deploy + Staging smoke.
4. H1–H3 → **H4–H5** via `verify_connectivity.sh` + live UJ-057/058.
5. Later: promote `stage`→`main` only after Staging gate green + re-approve (`D-S067-promote=2b`).

## Sign-Off

- [x] User approved implementation (11) — `D-S067-11-ac=1a`
- [x] Resume 12 — `D-S067-12-resume=1a`
- [x] Scope unchanged — `D-S067-12-scope=1a`
- [x] Risks approved — `D-S067-12-risks=1a`
- [x] Rollback + merge → 13 — `D-S067-12-merge=1a`
- [x] Ready for 13-deploy-smoke after merge + Staging CD green
