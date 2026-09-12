# Deploy Checklist — S014 / EV-010 (stage 12-verify-deploy, T6.4)

> Generated: 2026-07-19  
> Status: **approved + merged + Render deployed** (2026-07-19)  
> Deployment plan: `docs/deploy.md` (PyPI + Render) + execution-plan §Tech Stack  
> Merge tip: `c73e0ad` on `main` (PR #726)  
> PR: **#726** https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/726 — **MERGED**

## Target topology (unchanged)

| Role | Render service | URL |
|------|----------------|-----|
| API | `metar-to-iwxxm-api` | https://metar-to-iwxxm-api.onrender.com |
| Frontend | `metar-to-iwxxm-frontend-v4-web` | https://metar-to-iwxxm-frontend-v4-web.onrender.com |
| Worker | `metar-to-iwxxm-worker` | untouched this cycle (no F8 delta) |

Deploy mode: **image** (`ci-cd.yml` → GHCR `main-latest` + Render hooks on **main** push).  
PyPI: **independent** of Render via `.github/workflows/pypi-publish.yml` on version tags.

## Delta scope (what this deploy changes)

| Surface | Change |
|---------|--------|
| `apps/backend` | msgspec response encode (ADR-026); F2 → Rust `validate_iwxxm` SDK |
| `apps/frontend` | OpenAPI/client types for msgspec response shapes |
| `packages/tac-validate` | domain depth + CLI + wheel publish prep |
| `packages/iwxxm-validate` | Rust core + schema subset + CLI |
| `packages/tac2iwxxm` | `[validate]` extra |
| `packages/shared` | xsdata `iwxxm_xsd` models (ADR-027) |
| `.github/workflows/pypi-publish.yml` | OIDC matrix publish (new) |
| Secrets / CORS / migrations | **No new** CORS knobs or DB migrations; existing `METAR_CORS_ORIGINS` / `VITE_*` matrix still applies |

## Pre-deploy checks

| Area | Status | Evidence |
|------|--------|----------|
| Configuration complete | PASS | `docs/deploy.md` PyPI + Render sections; no `Needs human input` gaps for Render path |
| Secrets (Render) | PASS | No new Render secrets; existing Supabase/CORS/VITE matrix current |
| Secrets (PyPI OIDC) | **BLOCKED for live tag** | Workflow has `id-token: write`, no `PYPI_API_TOKEN`; **Trusted Publisher** must be configured on PyPI for each of 3 projects before first tag publish (operator) |
| Data / volumes / migrations | N/A | No DB schema changes |
| Resource allocation | PASS | Same Render services/plans; native wheels built in GHA not on Render |
| H0c CORS unit tests | PASS | 14 passed (policy + msgspec CORS) — re-run 2026-07-19 |
| `VITE_*` ↔ API URL matrix | PASS | `staging-secrets-matrix.md` + live `/config.json` `baseUrl`/`corsOrigins` match FE URL |
| `METAR_CORS_ORIGINS` documented | PASS | Live prod `corsOrigins` = frontend URL (2026-07-19) |
| Live health (current prod) | PASS | API `/health` **200**; FE `config.json` **200** |
| Live H4–H5 (pre-redeploy) | **FAIL / drift** | Staging drift + prior H4 CORS fail recorded in workflow-state; **re-run after msgspec redeploy at 13** (QA-S014-001) |
| Connectivity scripts | PASS | `verify_connectivity.sh` + `test_staging_connectivity.py` present |
| 11-verify-impl | PASS | F11–F14 + UJ-022/023/DEV-005 approved (`verify-impl.md`) |
| Package boundaries | PASS | tac-validate / iwxxm-validate / tac2iwxxm boundaries spot-check clean |
| Package versions | PASS | all three at `0.1.0`; `[validate]` extras declared |
| PyPI workflow dry-run | PASS | T4.4 checklist; `workflow_dispatch.publish` default false |
| Hard perf gates at publish | **DEFERRED** | Soft benches recorded; hard 0.85×/1.0× at T6.6 / tag time |
| Evolve PR | **MERGED** | [#726](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/726) @ `c73e0ad`; Deploy SUCCESS |

## PyPI Release Checklist (stage-12 slice)

```
PyPI Release Checklist: BLOCKED (Trusted Publisher) | CI READY

Package: tac-validate | iwxxm-validate | tac2iwxxm
Tag: *-v0.1.0 (first release)
OIDC: workflow ok | Trusted Publisher missing (operator)
Boundaries: ok
Hard gates: deferred to T6.6 at tag
Blockers: configure PyPI Trusted Publisher ×3; then tag after merge
Next: open evolve PR → merge → Render 13 → tag when Publisher ready
```

## Failure modes & mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Merge/deploy without msgspec FE types | Ship FE + API same PR; deploy API then frontend | mitigated by sequence |
| 2 | CORS regression after msgspec | H0c green; post-deploy `verify_connectivity.sh` H4–H5 at 13 | mitigated |
| 3 | Staging drift / stale image | Merge → main rebuilds GHCR + Render hooks; confirm tip after deploy | mitigated |
| 4 | Image build / maturin fail in CI | PR CI must be green before merge (ci-after-push) | pending PR |
| 5 | Double heavy validate layers | F11.4 orch dedupe + T3.8 tests | mitigated |
| 6 | Accidental PyPI publish | `publish` default false; tag-only + Trusted Publisher gate | mitigated |
| 7 | Tag publish before Trusted Publisher | Checklist BLOCKED until operator configures OIDC on PyPI | **accepted until configured** |
| 8 | Hard perf gate miss at tag | Soft benches in-cycle; hard fail at T6.6 before publish job succeeds | planned |
| 9 | Rollback needed | Redeploy prior Render deploy / GHCR image; PyPI versions immutable (yank only if needed) | documented below |

## Rollback

- **Render**: Dashboard or API → redeploy previous deploy for `metar-to-iwxxm-api` then frontend → re-run `verify_connectivity.sh` + `/health`.
- **PyPI**: Versions are immutable; do not re-tag. Yank only if critical; fix forward with `0.1.1+`.
- **Data**: no migrations → image-only rollback.
- **Last known good (pre-EV-010)**: current prod on `main` (drift vs branch tip; record SHA at merge time before 13).

## Recommended sequence (T6.4 → T6.5 → T6.6)

1. Commit session reports (`verify-impl.md`, `deploy-checklist.md`, plan/state) on evolve branch.
2. Push branch; open PR `[EV-010] F11–F14 — package publish + validation stack` → `main`.
3. Watch CI green; **user merge approval**.
4. Stage **13**: Render redeploy (API then FE) → H1–H5 + H6′ UJ-022.
5. Operator: configure PyPI Trusted Publisher ×3.
6. Tag `tac-validate-v0.1.0` / `iwxxm-validate-v0.1.0` / `tac2iwxxm-v0.1.0` (separately) → T6.6 hard gates + install smokes.

## Sign-Off

- [x] User approved implementation (11-verify-impl — F11–F14 + journeys)
- [x] User approved deploy strategy + rollback (2026-07-19 — 1A / D-S014-EV010-t64-deploy-A)
- [x] Evolve PR open (#726) — CI green; merged (D-S014-EV010-t64-merge-A)
- [x] Ready to merge / deploy (explicit approval) — Render 13 smokes PASS
- [ ] PyPI Trusted Publisher configured (blocker for tags only — not for Render 13)
