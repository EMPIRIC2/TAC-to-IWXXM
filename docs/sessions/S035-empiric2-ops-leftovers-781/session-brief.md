# Session brief — S035-empiric2-ops-leftovers-781

| Field | Value |
|-------|--------|
| **Session** | `S035-empiric2-ops-leftovers-781` |
| **Type** | `feature` (general evolve — no new Fn) |
| **Orchestrator** | `16-evolve` → **EV-028** |
| **Issue** | [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781) |
| **Branch** | `evolve/EV-028-empiric2-ops-leftovers-781` |
| **Opened** | 2026-08-01 |
| **UI preview** | N/A — no browser UI in scope |

## Intent

Finish EMPIRIC2 cutover leftovers on #781: purge Codecov from product CI/docs, point PyPI
Trusted Publishers at `EMPIRIC2/TAC-to-IWXXM` + `pypi-publish.yml`, prove OIDC with a small
tag publish, and rewrite public package landing READMEs so PyPI consumers do not need
internal ADR / Feature / E10 identifiers. Unblocks packaging work (#777); warm-up before a
product cycle.

## Intake lock (D-S035-open)

| ID | Choice | Meaning |
|----|--------|---------|
| 1b | feature + 16-evolve | EV-028 general cycle |
| 2a | Codecov + Trusted Publisher + landing READMEs | Out: e2e/load secrets, Render rename, Supabase Site URL, #777 publish |
| 3b | Three public packages + `dissemination` README | Consumer-facing; no ADR/Fn/E10 on landings |
| 4b | Configure + cut a small tag publish | Prove OIDC end-to-end |
| 5a | Lean+build routing | `00→16→01→02→04→07→08→10→13` |
| 6b | All three → `0.1.1` | `tac-validate`, `iwxxm-validate`, `tac2iwxxm` OIDC proof |

## In scope

1. **Codecov purge** — root + backend README badges; `codecov/codecov-action` steps in
   `.github/workflows/ci-cd.yml`; remove `.codecov.yml`; delete repo secret `CODECOV_TOKEN`;
   `main` CI green without Codecov.
2. **PyPI Trusted Publisher** — for `tac-validate`, `iwxxm-validate`, `tac2iwxxm`:
   Owner `EMPIRIC2`, Repository `TAC-to-IWXXM`, Workflow `pypi-publish.yml`, Environment `pypi`
   (replace stale `joseph-c-mcguire` / `metar-to-IWXXM` publishers).
3. **Tag publish proof** — bump at least one package past `0.1.0` (already on PyPI) and publish
   via tag → OIDC (see routing AskQuestion for which package(s)).
4. **Landing READMEs** — `packages/{tac-validate,iwxxm-validate,tac2iwxxm,dissemination}/README.md`
   rewritten for public/library consumers (install, API/CLI, boundaries); monorepo/internal
   tracing stays in corpus / session docs, not on PyPI long description.

## Out of scope

- Optional `e2e-tests.yml` / `load-tests.yml` secrets
- Render service/hostname rename to `tac-to-iwxxm-*`
- Supabase Site URL / redirect changes
- Publishing `iwxxm-dissemination` (#777) — README polish only
- Product Fn / API / UI changes

## Success criteria

1. `main` (via PR) CI green without Codecov steps; `CODECOV_TOKEN` removed.
2. Trusted Publishers on all three PyPI projects point at EMPIRIC2 + `pypi-publish.yml`.
3. At least one new version tag publishes successfully via OIDC.
4. Public package READMEs (incl. dissemination) have no required ADR/Feature/E10 references.
5. #781 closable for Codecov + PyPI leftovers (optional secrets remain optional).

## Related

- Prior ops: S022-rename-cutover (primary GHCR/Render cutover done)
- PyPI bootstrap notes: `docs/sessions/S014-package-publish-validation/reports/pypi-bootstrap-token.md`
  (publisher owner/repo values are stale — update in this cycle)
- Unblocks: #777 `iwxxm-dissemination` publish (separate cycle)
