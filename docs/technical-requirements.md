# Technical requirements

> Index: [README.md](README.md) 
> Last updated: 2026-11-24

This document states functional and technical requirements, required decisions,
and pass criteria. Behavioral product scope lives in
[product-requirements.md](product-requirements.md). Component layout lives in
[architecture.md](architecture.md). Environment names live in
[env-variable.md](env-variable.md).

**Authoritative NFR matrix for the open rebaseline:**
[non-functional-requirements.csv](non-functional-requirements.csv)
(epic [#1688](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1688)).
Where TR rows below disagree with that CSV, the CSV wins until Build updates
this table.

## How to use this document

1. Read the requirement id.
2. Make sure that the pass criterion is clear.
3. Make sure that the linked test id exists in [test-plan.csv](test-plan.csv) when one exists.
4. Change satellites under `deploy/` or the SBOM when runtime topology changes.

## Satellites (detail tables)

| Surface | Path | Owns |
|---------|------|------|
| Environment names | [env-variable.md](env-variable.md) | Exact env var spelling by consumer |
| Runtime deploy profiles | [config/deploy/profiles/](../config/deploy/profiles) | Non-secret local, staging, prod, and e2e JSON |
| Conversion profiles | [config/profiles/](../config/profiles) | Semantic and exchange catalog for the API |
| Rule catalogs | [config/rules/](../config/rules) | Issue catalog and provenance map |
| Coverage inventories | [config/engineering/](../config/engineering) | Unit coverage surface inventories |
| DOKS manifests | [config/deploy/doks/](../config/deploy/doks) | Staging and prod topology |
| SBOM | [config/sbom/cyclonedx.json](../config/sbom/cyclonedx.json) | Allowed dependency inventory |
| Quality tooling | [config/tooling/](../config/tooling) | Config for import-linter, Knip, dependency-cruiser, and the other quality tools (see [Quality tooling inventory](#quality-tooling-inventory)) |

## Platform requirements

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-P01 | Host API, frontend, and worker on DigitalOcean Kubernetes Service (DOKS) | Staging and prod manifests under `config/deploy/doks/` match running services |
| TR-P02 | Store shared/public and live-eval data in DigitalOcean Postgres via `DATABASE_URL` | Worker and live-eval writes use DO Postgres (NFR-002 / FR-065) |
| TR-P06 | Refresh live-map evaluation snapshot on a ~15 minute schedule (staging and prod); serve via public `GET /api/v1/live-map/eval` | Cron/job interval matches env; GET returns latest `computed_at` without recomputing on pan (FR-045 / D-027) |
| TR-P03 | Use Supabase for Auth and user/history (PostgREST allowed for user data) | Auth + user history on Supabase; shared data on DO Postgres (C1 / NFR-003) |
| TR-P04 | Keep public convert, lint, validate, and decode reachable with API keys (no user JWT); dissemination routes removed in rebaseline | Live and unit tests call public routes with API key policy (NFR-007); no disseminate surface |
| TR-P05 | Gate long-term work sessions on Auth JWT | `/api/v1/work-sessions*` rejects anonymous writes |

## Quality gates

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-Q01 | Unit coverage is **100%** line and branch on packages and apps | `fail_under = 100` holds in CI |
| TR-Q02 | Every `scripts/*.sh` maps to a bats test | Script coverage inventory matches files |
| TR-Q03 | Frontend Vitest coverage stays at 100% global thresholds | `pnpm --filter @metar/frontend run test:coverage` passes |
| TR-Q04 | Contract and mutation gates stay in CI | Contract and mutation jobs run on the required schedules |
| TR-Q05 | Wave 1 quality tools run fail-closed in CI (import-linter, per-member deptry, dependency-cruiser, Knip, oasdiff, Schemathesis, coverage denominator audit) | `make check-fast` and the quality-tooling CI job pass on PRs to `stage` (TC-QV-001 to TC-QV-009) |
| TR-Q06 | Do not exclude whole hand-written files or directories from lint, typecheck, or coverage; prefer line-level ignores; generated trees (for example `iwxxm_xsd/v*`) may stay excluded when documented | Root and member configs have no whole-file hand-written omits; generated excludes are documented (TC-QV-008) |
| TR-Q07 | Pytest uses `--strict-config` and `xfail_strict`; the root `Coverage collection returned no data` warning filter is mutation-local only | Root `pyproject.toml` matches; mutation script keeps the advisory `-W` (TC-QV-009) |
| TR-Q08 | Wave 2 security scanners (OSV-Scanner, Gitleaks, actionlint) run in CI; OpenGrep project baseline stays required | Security workflow or quality-tooling companion posts results; clear violations fail the job (TC-QV-010 to TC-QV-012) |

### Quality tooling inventory

No standing dependency inventory file exists. [config/sbom/cyclonedx.json](../config/sbom/cyclonedx.json)
is the live inventory. Run `make sbom` after the tool pins land, then commit the result.
Tool configs live in [config/tooling/](../config/tooling). Do not add copies at the
repository root.

| Tool | Wave | Requirement | Scope | State |
|------|------|-------------|-------|-------|
| import-linter | 1 | TR-Q05 | Python layer contracts | Config and CI job landed |
| deptry | 1 | TR-Q05 | Python dependency use, per workspace member | Pinned with per-member config and CI |
| dependency-cruiser | 1 | TR-Q05 | Frontend import rules | Pinned with config and CI |
| Knip | 1 | TR-Q05 | Unused frontend files and exports | Pinned with config and CI |
| oasdiff | 1 | TR-Q05 | OpenAPI breaking-change diff against `docs/api/` | Script and CI landed |
| OSV-Scanner | 2 | TR-Q08 | Known vulnerabilities in lockfiles | Install script updated; CI planned |
| Gitleaks | 2 | TR-Q08 | Secret scan (config exists) | Install script updated; CI planned |
| actionlint | 2 | TR-Q08 | GitHub Actions workflow lint | Install script updated; CI planned |
| Vulture | 2 | None yet | Dead Python code | Planned, advisory |
| jscpd | 2 | None yet | Duplicate code | Planned, advisory |
| Radon | 2 | None yet | Python complexity | Planned, advisory |

Vulture, jscpd, and Radon stay advisory until a clean baseline exists. Add a TR row
when one of them becomes fail-closed. Tools not listed here are deferred and have no
requirement id.

## Conversion and validation

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-C01 | Convert TAC through `packages/tac2iwxxm` only for HTTP convert | Backend convert path does not reintroduce GIFTs |
| TR-C02 | Lint TAC through `packages/tac-validate` | Lint responses use the issue catalog |
| TR-C03 | Validate IWXXM through `packages/iwxxm-validate` with official Schematron + matching XSD | Shared quality-bar regression covers pins `3.0`, `2021-2`, `2023-1`, `2025-2` (FR-032 / NFR-017) |
| TR-C04 | Do not hand-edit schema trees; treat `vendor/schemas/` as optional materialization only | No hand edits; acquisition SoT is `config/schemas/iwxxm-official-pins.json` (FR-077 / NFR-016) |
| TR-C05 | Fetch official IWXXM pins at build or runtime with hash verify | `make fetch-iwxxm-schemas` (or CI equivalent) populates cache; missing pin fails closed |
| TR-C06 | Keep `vendor/manifest.json` for optional materialization / legacy sync | When vendor trees are present, integrity checks still apply; they are not acquisition SoT |

## Dissemination and security

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-D01 | Keep bring-your-own-credentials destination secrets in memory only | No persistence to sessions, logs, or profiles |
| TR-D02 | Require non-empty `DISSEMINATION_EGRESS_ALLOWLIST` | Empty allowlist denies egress |
| TR-D03 | Mediate egress in the backend | Browser does not open raw sink sockets for push |
| TR-D04 | Do not auto-push from the ingest worker | Worker only stores or quarantines |

## Profiles and domain catalogs

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-R01 | Keep semantic and exchange profiles distinct | Resolver behavior matches [domain-contract.md](domain-contract.md) |
| TR-R02 | Ship the conversion profile catalog in the API image | Dockerfile copies `config/profiles`; catalog GET succeeds |
| TR-R03 | Keep lint issue catalog and provenance map under `config/rules/` | Drift tests and provenance canary pass |
| TR-R04 | Follow TAC lint, convert, XSD, then Schematron for quality bars | Domain contract pipeline gates hold |

## Engineering clarity and coverage

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-E01 | Prefer clear English names on new public package symbols | Package facade tests pass for listed start-here imports |
| TR-E02 | Keep coverage surface inventories under `config/engineering/` | Coverage inventory unit tests pass |
| TR-E03 | Do not put ticket or session ids in public import paths | Package READMEs and `__all__` stay free of those ids |
| TR-E04 | Root `pyproject.toml` is the single source of truth for Ruff, pytest, coverage, and basedpyright; third-party `[project]` / `[dependency-groups]` entries use exact `==` pins from `uv.lock` | `scripts/ci/check-exact-pins.py` passes; member packages inherit root tool tables (extend or omit duplicates) |

## WMO membership and native crates

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-W01 | Harvest WMO membership from checked-in vendor data | Pull-request CI does not fetch live `codes.wmo.int` HTML |
| TR-W02 | Keep Rust hot paths under package `rust/` trees | `make rust-check` and CI cargo/maturin jobs pass |

## Local dissemination test setup

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-B01 | Provide Compose profile `mock-byoc` for local SQL end-to-end tests | `make test-e2e-f16-live-sql` passes with documented allowlist and CORS |

## Parity checklist

When you change runtime, config, or deploy topology:

1. Match env names to [env-variable.md](env-variable.md).
2. Match service names to [config/deploy/doks/](../config/deploy/doks).
3. Add new libraries to the SBOM, or stop and decide first.
4. Keep component boundaries aligned with [architecture.md](architecture.md).
5. Record non-obvious trade-offs in the local decision log or [decisions.csv](decisions.csv).

## Related contracts

- Domain: [domain-contract.md](domain-contract.md)
- HTTP narrative: [api-contract.md](api-contract.md)
- Ops: [ops-contract.md](ops-contract.md)
- Integration: [integration-contract.md](integration-contract.md)
- Data: [data-flows.md](data-flows.md), [data-integrations.md](data-integrations.md)
