# Technical requirements

> Index: [README.md](README.md) 
> Last updated: 2026-11-10

This document states functional and technical requirements, required decisions,
and pass criteria. Behavioral product scope lives in
[product-requirements.md](product-requirements.md). Component layout lives in
[architecture.md](architecture.md). Environment names live in
[env-variable.md](env-variable.md).

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
<<<<<<< HEAD
| DOKS manifests | [deploy/doks/](../deploy/doks) | Staging and prod topology |
| SBOM | [config/sbom/cyclonedx.json](../config/sbom/cyclonedx.json) | Allowed dependency inventory |
=======
| DOKS manifests | [config/deploy/doks/](../config/deploy/doks) | Staging and prod topology |
| SBOM | [sbom/cyclonedx.json](../sbom/cyclonedx.json) | Allowed dependency inventory |
>>>>>>> 6d387ec7 (docs: move deploy under config and rename user-docs to github-wikia)

## Platform requirements

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-P01 | Host API, frontend, and worker on DigitalOcean Kubernetes Service (DOKS) | Staging and prod manifests under `config/deploy/doks/` match running services |
| TR-P02 | Store product data in DigitalOcean Postgres via `DATABASE_URL` | Work sessions and worker writes use DO Postgres, not Supabase DB |
| TR-P03 | Use Supabase only to verify Auth JWTs | Auth routes verify JWT; no product PostgREST dependency |
| TR-P04 | Keep public convert, lint, validate, and disseminate routes free of JWT | Live and unit tests call those routes without Bearer tokens |
| TR-P05 | Gate long-term work sessions on Auth JWT | `/api/v1/work-sessions*` rejects anonymous writes |

## Quality gates

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-Q01 | Unit coverage is **100%** line and branch on packages and apps | `fail_under = 100` holds in CI |
| TR-Q02 | Every `scripts/*.sh` maps to a bats test | Script coverage inventory matches files |
| TR-Q03 | Frontend Vitest coverage stays at 100% global thresholds | `pnpm --filter @metar/frontend run test:coverage` passes |
| TR-Q04 | Contract and mutation gates stay in CI | Contract and mutation jobs run on the required schedules |

## Conversion and validation

| ID | Requirement | Pass criterion |
|----|-------------|----------------|
| TR-C01 | Convert TAC through `packages/tac2iwxxm` only for HTTP convert | Backend convert path does not reintroduce GIFTs |
| TR-C02 | Lint TAC through `packages/tac-validate` | Lint responses use the issue catalog |
| TR-C03 | Validate IWXXM through `packages/iwxxm-validate` | XSD and Schematron run for supported pins |
| TR-C04 | Consume vendor schemas read-only | No hand edits under `vendor/schemas/` |
| TR-C05 | Pin IWXXM lines through `vendor/manifest.json` | Convert and validate select an existing pin |

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
