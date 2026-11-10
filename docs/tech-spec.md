# Technical specification hub

> **Corpus ID:** `tech-spec` — see [AGENTS.md](../AGENTS.md).  
> **Architecture / components:** [spec.md](spec.md) (`system-spec`).  
> **Last updated:** 2026-11-10 (EV-repo-docs-cleanup — profiles, SBOM, env-variable)

This hub points to the documents that define runtime, configuration, deployment,
and allowed dependencies. Those satellite documents hold the long tables.
Do not copy those tables into this file.

## How to use this hub

1. Find the topic in the **Satellites** table below.
2. Open that document for exact field names, environment variable names, and
   deploy steps.
3. Check the **Parity checklist** when you change runtime or deploy behavior.

## Satellites

| Doc | What it owns |
|-----|----------------|
| [env-variable.md](env-variable.md) | Env var names, who consumes them (API / frontend / CI) |
| [deploy/profiles/](../deploy/profiles/) | Non-secret `local` / `staging` / `prod` / `e2e` JSON |
| [deploy/doks/](../deploy/doks/) | DOKS staging/prod topology and manifests |
| [sbom/cyclonedx.json](../sbom/cyclonedx.json) | Live CycloneDX inventory; `make sbom` + CI drift gate |

## Related corpus

| Doc | Role |
|-----|------|
| [spec.md](spec.md) | System architecture, component map, hard constraints |
| [api-contract.md](api-contract.md) | HTTP routes and payloads |
| [../api/openapi.json](../api/openapi.json) | Machine-readable OpenAPI |
| Local `docs/adr/` | Architecture decisions that constrain tech choices (opt-in) |

## Coverage gate (ADR-007 / EV-080)

Unit coverage is a hard gate: **100%** line and branch on packages and apps
(`fail_under = 100`). Script coverage covers `scripts/**/*.py` and maps every
`scripts/**/*.sh` to a bats file under `tests/bats/`. See [test-plan.md](test-plan.md)
§EV-080 / TC-EV080-009.

## Parity checklist (quick)

When you change runtime behavior, configuration, or deploy topology:

1. Confirm that each environment variable name exists in **env-variable** with
   the same spelling.
2. Confirm that deploy topology and service names match **deploy/doks**.
3. Confirm that each new library appears in the **SBOM**, or raise AskQuestion
   before you add it.
4. Confirm that component boundaries still match **spec.md** §Component Overview.
5. If the change is a non-obvious trade-off, add or cite a local architecture
   decision record (**ADR**).

## Weekly staging validation catalog (CI quality window)

A scheduled GitHub Actions workflow runs every Sunday at 00:00 UTC. The workflow
probes staging catalogs and fixture lint/validate runs, then uploads a report
artifact. Detail: [env-variable.md](env-variable.md) §CI. This window adds no
new runtime dependency. [Corpus: product §F2] [Corpus: product §F15]

## WMO membership harvest (F12 deepen)

Offline L3 token membership for the TAC lint package `tac-validate` uses
checked-in vendor data. Pull request CI must **not** fetch live
`codes.wmo.int` HTML.

| Surface | Location |
|---------|----------|
| SoT (CSV `notation`) | `vendor/schemas/iwxxm-codelists/CSV/**/*_entity.csv` |
| SoT (nil RDF) | `vendor/schemas/iwxxm/{pin}/IWXXM/rule/codes.wmo.int-{common,iwxxm}-nil.rdf` |
| Pin / cadence | `vendor/manifest.json` → `iwxxm-codelists`; refresh on normal vendor sync PRs |
| Snapshot fetch | `scripts/vendor/sync_iwxxm.py` |
| Artifact | `packages/tac-validate/src/tac_validate/data/wmo_membership.json` |
| Harvest module | `packages/tac-validate/src/tac_validate/membership.py` |
| CLI | `scripts/iwxxm/harvest_wmo_membership.py` |
| Regenerate | `make membership-regen` |
| Drift check | `make membership-check` |

Test IDs: [test-plan.md](test-plan.md) §EV-050 / TC-EV050-001..003.

## Rust native crates (F13 / F14)

Hot-path Rust code lives under `packages/tac2iwxxm/rust` and
`packages/iwxxm-validate/rust` (PyO3 / maturin).

| Surface | Location |
|---------|----------|
| Remote CI | `.github/workflows/ci-cd.yml` — cargo crate matrix + maturin packages |
| Local mirror | `make rust-check` |
| Test IDs | [test-plan.md](test-plan.md) §EV-045 / TC-EV045-*; journey UJ-DEV-006 |

## Local mock BYOC / live SQL e2e (F16)

Bring Your Own Credentials (BYOC) means the operator pastes destination secrets
for one send. Those secrets stay in memory only.

| Piece | Location |
|-------|----------|
| Overlay | `docker-compose.yml` profile `mock-byoc` |
| Compose project | `-p metar-iwxxm-mock-byoc` (via `BYOC_COMPOSE`) |
| Make | `compose-mock-byoc-up` / `compose-mock-byoc-down`; `*-all-*` with wis2box |
| Live suite | `make test-e2e-f16-live-sql` |
| Flag | `F16_LIVE_SQL` — default **1** locally, **0** when `CI` is set |
| Allowlist | `DISSEMINATION_EGRESS_ALLOWLIST` — see [env-variable.md](env-variable.md) |
| Fixtures | `tests/fixtures/byoc/mock-byoc-destinations.json` |

### Local harness recipe (CORS + allowlist)

```bash
export DISSEMINATION_EGRESS_ALLOWLIST=wis2box,127.0.0.1,127.0.0.0/8,localhost
export METAR_CORS_ORIGINS=http://localhost:18000,http://127.0.0.1:18000
# Or rely on deploy/profiles/local.json corsOrigins: ["http://localhost:18000"]

make test-e2e-f16-live-sql
```

The running API must have `DISSEMINATION_EGRESS_ALLOWLIST` set (empty ⇒ deny).
Restart the local API after you export the recipe above.
