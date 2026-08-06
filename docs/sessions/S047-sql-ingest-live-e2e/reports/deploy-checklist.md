# Deploy Checklist — S047 / EV-039 (12-verify-deploy)

> Generated: 2026-08-06  
> Status: **APPROVED** (`D-S047-12`=1) — push + PR; 13 after CI/CD (H4–H5 required)  
> Prior: 11 **APPROVED** (`D-S047-11`=1)  
> Deployment: [docs/deploy.md](../../../deploy.md) · DOKS CD on `main`  
> Tip: `cfe1236b` · PR [#891](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/891)  
> `env_role`: **live = prod** (sole DOKS stack `api|app.tac-to-iwxxm.com`)  
> Corpus: `[Corpus: tech-spec]` · `[Corpus: product §F16]` · `[Corpus: tests]` · connectivity-gates §12–13  
> **CI note:** Branch pushed; local pre-push `make ci` green. GitHub Actions has **not** started check suites on #891 (only Cursor suite queued) — tip CI gate blocked until runs appear or waived.

## Scope (delta)

| Surface | Change | Deploy action |
|---------|--------|---------------|
| `apps/e2e` + Makefile / Compose mock-byoc | LIVE SQL Playwright + teardown | **No prod SQL services** (F16-R9 OOS) |
| `packages/dissemination` `live_write_assert` | Test helper CLI for write assert | Ships in package image with API — **no new API routes** |
| `docker-compose.yml` | Local allowlist + CORS + `tmp/f16-live` volume | **Local/CI only** — not DOKS |
| `package.json` `js-yaml` pin ≥4.3.1 | GHSA pin | **FE rebuild** on merge via normal CD |
| Docs (feature-list, test-plan, tech-spec, journeys) | AC / TC-F16-LIVE / harness recipe | Docs only |
| Auth / CORS origins (prod) | Unchanged | Re-verify H4–H5 post-merge if FE ships |
| Worker / secrets / DB migrations | None | N/A |

**Live stack today:** DOKS @ `619a7ac3` (EV-038). This branch is ahead with harness + pin only — land via PR → `main` → CD.

## Pre-Deploy

- [x] Configuration complete — no new Render/DOKS SQL services; harness stays Compose profile
- [x] Secrets — no new keys (`DISSEMINATION_EGRESS_ALLOWLIST` already required for F16)
- [x] Data assets — N/A (no model weights)
- [x] Resource allocation — unchanged
- [x] Rollback — prior DOKS/GHCR tag / previous rollout
- [x] H0c CORS — `tests/unit/test_cors_policy.py` **6/6 PASS** (2026-08-06)
- [x] Connectivity scripts — `scripts/deploy/verify_connectivity.sh` present
- [ ] Branch pushed + tip CI green (`ci.yml` / project CI)
- [ ] PR to `main` opened
- [ ] Merge + CD (explicit user approval)
- [ ] Post-deploy H1–H3 + H4–H5 (or documented waive for harness-only)

## Failure Mitigations

| # | Risk | Mitigation | Status |
|---|------|------------|--------|
| 1 | Image/CD failure | CI on PR + DOKS Deploy job | pending push/PR |
| 2 | Accidental prod SQL containers | Scope OOS; checklist + session brief | **approved pattern** |
| 3 | Allowlist too open in prod | Prod allowlist separate from Compose defaults; ADR-029 fail-closed | **ready** |
| 4 | `js-yaml` pin breaks FE build | pnpm lock updated; CI build job | pending CI |
| 5 | SQL Server not verified on Mac | Documented waive (QEMU); CI skippable | **accepted** (`D-S047-11`) |
| 6 | CORS after FE rebuild | `verify_connectivity.sh` H4–H5 | planned at 13 |

## Rollback

- Roll back DOKS deployments to prior GHCR/DOKS tag (last green: `20260806144346-619a7ac`)
- Re-run `bash scripts/deploy/verify_connectivity.sh`
- No DB migrations this cycle
- Local: `make compose-mock-byoc-down` (includes `-v`)

## Recommended path (13)

1. **Push** `evolve/EV-039-sql-ingest-live-e2e` and wait tip CI green.
2. Open PR → `main`; wait PR CI green.
3. **Merge** (explicit user approval).
4. Wait DOKS CD (API + FE for `js-yaml` pin).
5. H1–H3 → **`bash scripts/deploy/verify_connectivity.sh`** (H4–H5).
6. Optional: mocked H6′ already green locally; LIVE SQL remains **local/CI opt-in** (not prod SQL).

## Sign-Off

- [x] User approved implementation (11 / `D-S047-11`)
- [x] User approved deploy strategy (this checklist / `D-S047-12`=1)
- [x] Ready to push / PR / 13-deploy-smoke (merge still needs explicit approval)
