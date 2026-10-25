# Context — config file hygiene

**Session:** `EV-config-file-hygiene`
**Mode:** scoped
**Gate:** documenting → implementing **closed**
**Baseline:** current workspace tree on 2026-10-25

[Corpus: tech-spec] [Corpus: tech-spec §config-spec] [Corpus: deploy] [Corpus: product §M5]

## Goal

Classify each in-scope Brewfile, YAML, JSON, TOML, and shell file as keep, update, merge, or delete. Approved edits must keep CI, deploy, and local-setup behavior.

## Out of scope

- `.tools/`, coverage JSON, `artifacts/`, `evidence/`, `htmlcov/`
- Test fixtures, quality-matrix testdata, and package `examples/`
- Domain data under package `src/` (lint policies, decode packs, emit maps)
- `vendor/schemas`, lockfiles, generated OpenAPI, `.env`
- `.cursor/` and `.claude/` (operator declined this fence)
- `docs/domain/` catalogs and `docs/engineering/` inventories
- Product conversion, validation, and operator UI behavior

## In scope

176 files. Full paths: session report `reports/config-inventory.txt` (not a design gate).

| Group | Count | Role |
|-------|------:|------|
| `.github/workflows/` | 29 | CI and scheduled checks |
| `scripts/**/*.sh` | 52 | CI, deploy, env, security, supabase, vendor helpers |
| `deploy/doks/` | 33 | Kubernetes base + staging/prod overlays |
| Package and app manifests | 22 | `pyproject.toml`, `package.json`, `tsconfig.json`, `Cargo.toml`, app `pyrightconfig.json` |
| Root toolchain | 11 | `Brewfile`, `pyproject.toml`, `ruff.toml`, `package.json`, `pnpm-workspace.yaml`, `pyrightconfig.json`, `.pre-commit-config.yaml`, `.yamllint.yml`, `.gitleaks.toml`, `start-dev-servers.sh` |
| Compose and Render | 4 | `docker-compose.yml`, `docker-compose.wis2box.yml`, `docker-compose.mock-byoc.yml`, `render.yaml` |
| Runtime JSON | 4 | `config/local.json`, `config/prod.json`, `config/staging.json`, `config/e2e.json` |
| Monitoring | 6 | Prometheus, Loki, Grafana |
| Other | 15 | App launch shells, `supabase/config.toml`, `workflows/f8-metar-ingest-default.yaml` |

Counts are from the 2026-10-25 inventory. Requirements will classify each file; this brief only records the fence and the first contradictions.

## Users and journeys

Maintainers and agents. No user journey changes. No browser UI. No PII or retention change. H4–H5 stay out. H0 applies only if a workflow file changes.

## Standing docs

Delta only, and only when a path or command actually changes:

- [Corpus: tech-spec] `docs/config-spec.md`
- [Corpus: deploy] `docs/deploy.md`
- [Corpus: tech-spec] `docs/dependency-inventory.md` when a Brewfile or manifest pin moves

Do not rewrite [Corpus: product], journeys, or the API contract for this pass.

## Findings to resolve in requirements

These are observations, not approved deletions.

| ID | Observation | Why it matters |
|----|-------------|----------------|
| R1 | `config-spec.md` says `METAR_CONFIG_ENV` is `local` or `prod`, and that Render is suspended in favor of DOKS. `config/staging.json`, `config/e2e.json`, and `render.yaml` still exist. `docs/deploy.md` still lists `render.yaml`. | A delete of `render.yaml` or the extra JSON files is a doc and deploy decision, not an obvious unused file. |
| R2 | About fifteen product-family workflows (`metar-quality.yml`, `taf-quality.yml`, and siblings) each call a matching `scripts/ci/run_*_quality.sh`. | Same shape, different path filters and check names. Collapsing them would change GitHub check identity. Default is keep unless branch protection is updated in the same change. |
| R3 | `apps/backend/scripts/start_dev.sh` exports `DISABLE_AUTH=true` and listens on port `8002`. [Corpus: tech-spec §config-spec] marks `DISABLE_AUTH` retired. The port standard in that spec is API `18001`. | Strong update-or-delete candidate. Must confirm no caller still uses it. |
| R4 | `scripts/launchers/launch_api.sh` sets `REPO_ROOT` to the parent of `scripts/launchers`, which is `scripts/`, and defaults the API port to `8001`. `start-dev-servers.sh` is the documented launcher (`config-spec.md` cites it). | Likely stale next to the root launcher. Confirm callers before delete. |
| R5 | `deploy/doks/overlays/staging/` and `prod/` repeat ingress, configmap, and redirect patches. | Kustomize overlays are supposed to differ by environment. Do not merge them into one file. |
| R6 | `Brewfile` is the only Homebrew manifest. It already points at `docs/deploy.md` and `docs/ops/DEVELOPMENT.md`, and it refuses to install pnpm because corepack owns that pin. | Keep. Review comments against current formulae only if a pin is wrong. |
| R7 | Root `ruff.toml` and root `pyproject.toml` are both present. | Likely an intentional split. Merge only if one file can own the settings without changing lint behavior. |

## Memory

Engineering-memory retrieve did not run. Neo4j at `bolt://localhost:7687` was unavailable. Cross-project checkpoint: **skip**.

## Next

`spec-development/requirements` — lock the classification rules, then the per-file keep / update / merge / delete list. Build stays blocked.
