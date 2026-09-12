---
session_id: S022-rename-cutover
type: ops
status: completed
completed_at: 2026-07-27
branch: infra/S022-rename-cutover
started_at: 2026-07-27
intent: "ops: finish EMPIRIC2/TAC-to-IWXXM rename cutover (Render, GHCR, secrets, PyPI) — #781; unlock live H4–H5 / UJ-032 goldens deferred from S021"
orchestrator: 15-service-health
evolve_cycle_id: null
context_briefs:
  - docs/context/rename-cutover-781.md
standing_docs_touched:
  - docs/deploy.md
  - docs/tech-spec.md
  - docs/deploy-state.md
github_issue: 781
prior_session: S021-golden-examples-ui
---

# Session S022 — rename-cutover

## Intent

Finish the **EMPIRIC2 / TAC-to-IWXXM** infra rename cutover so live Render services pull
`ghcr.io/empiric2/tac-to-iwxxm/*`, worker builds from the new repo URL, and optional secrets /
PyPI Trusted Publishers are updated — unblocking deploys and the **live H4–H5 / UJ-032
goldens** proof deferred from S021 / EV-016
([#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781)).

No product feature work. Keep live hostnames (`metar-to-iwxxm-*.onrender.com`) unless a
separate DNS/CORS decision is approved.

## Prior session

| Item | Disposition |
|------|-------------|
| S021 / EV-016 | **Completed** — F7.g on `main` @ `c49f22b` (PR #782); live H4–H5 **waived** → #781 (`D-S021-EV016-13-waive-live-h4h5`) |
| Issue #780 | Closed |
| Live FE | Still pre–F7.g (`joseph-c-mcguire` GHCR imagePath) |

## Classification

| Field | Value |
|-------|-------|
| Session type | **`ops`** (infra cutover; no Fn / no product AC) |
| Orchestrator | **15-service-health** (cutover verify + health) |
| Follow-on stage | **13-deploy-smoke** (redeploy + H4–H5 + UJ-032 goldens) |
| Preset | Ops override: `00 → 15 → 13` (not Lean product evolve) |
| Branch | `infra/S022-rename-cutover` (docs / deploy-state deltas only if needed) |

## Scope (proposed — pending approval)

### In (priority order)

1. **Confirm GHCR** — Empiric2 packages exist (`backend`/`frontend`/`worker`); visibility OK
2. **Render imagePath** — API + frontend → `ghcr.io/empiric2/tac-to-iwxxm/{backend,frontend}:main-latest`
3. **Worker repo URL** → `https://github.com/EMPIRIC2/TAC-to-IWXXM`
4. **Redeploy** API / frontend / worker; confirm hooks fire
5. **Smoke** H0ci / H0c / H1–H3, then **H4–H5** + live **UJ-032** Examples (goldens)
6. **Secrets** — recreate missing Actions secrets only if those workflows are still in use
7. **PyPI** — Trusted Publisher → `EMPIRIC2/TAC-to-IWXXM` + `pypi-publish.yml` (may need org admin)
8. **Docs** — sync `[Corpus: tech-spec]` satellites (`deploy.md` / deploy-state) with new image paths

### Out

- Renaming Render service hostnames / CORS / frontend public URL (optional later)
- Recreating Supabase / OpenAIP / admin login
- Product quality bars (#731 AIRMET→SIGMET chain) or #777 `iwxxm-dissemination` publish
- Renaming local checkout dir or `@metar/*` npm scopes / `METAR_*` env names

## UI reference

Ops session — **no local UI preview** required. Live workbench goldens verification is part of
**13-deploy-smoke** after cutover (not a non-deployed preview).

## Success criteria (from #781 AC + S021 deferral)

1. `main` CI green on EMPIRIC2 without Codecov
2. Render API + frontend pull Empiric2 `main-latest` and pass health/smoke — **done**
3. Worker builds from EMPIRIC2 repo URL — **done**
4. Live H4–H5 + UJ-032 goldens Examples UI observed on production FE — **done**
5. PyPI Trusted Publishers updated (or explicitly deferred with owner note if admin-blocked) — **deferred** (follow-up on #781)

## Close

**Completed** 2026-07-27 — user option 1 (`D-S022-close-option1`). Session reports:
`reports/service-health.md`, `reports/deploy-smoke.md`.
