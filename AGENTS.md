# Agent documentation corpus

**Single source of truth for agent skills.** Before design, parity, scope, or
hotfix triage work, read the rows below that apply. Do not invent alternate
document sets.

> Skills and rules must cite paths from this file (for example
> `[Corpus: system-spec]`, `[Corpus: adr/ADR-00N]` when a local ADR copy exists).
>
> Default load is the **engineering spine** only. Local trees listed under
> **Local opt-in** are not in git. Keep them on disk for agent work when needed.

## Minimal corpus (design and parity)

Index: [docs/README.md](docs/README.md). Writing rules:
[docs/documentation-standards.md](docs/documentation-standards.md).

| ID | Role | Path | Skills use it to… |
|----|------|------|-------------------|
| **product** | Project definition and behavioral requirements | [docs/product-requirements.md](docs/product-requirements.md) (+ this file §Product feature index mirror) | Scope (feature `F*` / milestone `M*`); reject out-of-list work |
| **journeys** | End-user journeys | [docs/user-journeys.csv](docs/user-journeys.csv) + [docs/user-journeys.md](docs/user-journeys.md) | End-to-end / verify-impl sign-off (`UJ-*`) |
| **ui-style** | Living operator UI style guide | [docs/ui-style-guide.md](docs/ui-style-guide.md) | UI/UX tweak norms; cite when polishing the frontend |
| **system-spec** | Architecture, components, constraints | [docs/architecture.md](docs/architecture.md) | Design parity vs `apps/` + `packages/` + `vendor/` |
| **tech-spec** | Functional/technical requirements and pass criteria | [docs/technical-requirements.md](docs/technical-requirements.md) | Config names, environment, deploy topology, dependency pins |
| **api** | HTTP contract | [docs/api-contract.md](docs/api-contract.md) + [docs/api/openapi.json](docs/api/openapi.json) | Request / response / error shapes |
| **ops** | Ops contract | [docs/ops-contract.md](docs/ops-contract.md) | Local/staging/prod ops expectations |
| **domain** | Domain contract (profiles, lint/convert/validate order) | [docs/domain-contract.md](docs/domain-contract.md) + [config/profiles/](config/profiles/) + [config/rules/](config/rules/) | Semantic/exchange profiles and rule catalogs |
| **integration** | Integration contract | [docs/integration-contract.md](docs/integration-contract.md) | External system wiring |
| **data-flows** | Data paths | [docs/data-flows.md](docs/data-flows.md) | Flow order through convert/decode/session/ingest/disseminate |
| **data-integrations** | Data systems | [docs/data-integrations.md](docs/data-integrations.md) | Systems that supply or receive data |
| **tests** | Test matrix and gates | [docs/test-plan.csv](docs/test-plan.csv) + [docs/test-plan.md](docs/test-plan.md) | Parity checks, smoke test-case IDs, CI expectations |
| **raid** | Risks, assumptions, issues, decisions | [docs/risks.csv](docs/risks.csv), [docs/assumptions.csv](docs/assumptions.csv), [docs/issues.csv](docs/issues.csv), [docs/decisions.csv](docs/decisions.csv) | Evolve/RAID tracking |
| **doc-standards** | Documentation standards | [docs/documentation-standards.md](docs/documentation-standards.md) | STE + avoid-ai + corpus citation rules |
| **deps** | Live dependency inventory | [config/sbom/cyclonedx.json](config/sbom/cyclonedx.json) | Allowed packages; regenerate with `make sbom` |
| **env** | Environment variable names | [docs/env-variable.md](docs/env-variable.md) | Env var contract by layer |
| **changelog** | Release notes | [CHANGELOG.md](CHANGELOG.md) | Release history |

Compatibility pointers: `docs/spec.md` → architecture; `docs/tech-spec.md` → technical-requirements.

### Tech-spec satellites

| Path | Topic |
|------|--------|
| [docs/env-variable.md](docs/env-variable.md) | Environment variable contract |
| [config/deploy/profiles/](config/deploy/profiles/) | Non-secret runtime JSON (`local` / `staging` / `prod` / `e2e`) |
| [config/profiles/](config/profiles/) | ConversionProfile catalog (API image) |
| [config/rules/](config/rules/) | Issue catalog and provenance map |
| [config/engineering/](config/engineering/) | Coverage surface inventories |
| [config/deploy/doks/](config/deploy/doks/) | DOKS deploy manifests and operator notes |
| [config/sbom/cyclonedx.json](config/sbom/cyclonedx.json) | CycloneDX SBOM (CI drift-checked on push) |

## Local opt-in (not in git; keep local copies)

These paths stay on the developer machine. Clones do not receive them.

| Path | When |
|------|------|
| `docs/adr/` | Architecture decisions (`ADR-NNN`) — local only, not tracked |
| `docs/decisions/` | Interview / evolve decision logs |
| `docs/domain/`, `docs/engineering/`, `docs/ops/` | Domain mining, engineering notes, ops runbooks |
| `docs/guides/`, `docs/integration/`, `docs/policies/` | Guides and policy notes |
| `docs/bug-reports/`, `docs/context/`, `docs/ui-ux-tweaks/`, `docs/assets/`, `docs/ste/` | Hotfix, context dumps, UX logs, STE dictionary |
| `docs/local-feeders/` | Full legacy dumps |

Machine catalogs for profiles, rules, and coverage inventories live under
`config/` and stay tracked.

## Product feature index

Canonical behavioral table:
[docs/product-requirements.md](docs/product-requirements.md).
This section mirrors feature ids for quick agent load.

| # | Feature | Status |
|---|---------|--------|
| F1 | METAR → IWXXM conversion (GIFTs-era UX) | Superseded by F6 |
| F2 | IWXXM validation | Implemented |
| F3 | Airport data services | Implemented |
| F4 | IWXXM version handling | Implemented |
| F5 | User METAR work history | Implemented |
| F6 | General TAC→IWXXM (`tac2iwxxm`) | Implemented |
| F7 | Multi-product TAC operator UI / sessions | Implemented (shell: Convert, Live map, History, Rule catalogs, Code names; Station health in progress) |
| F8 | Near-realtime TAC ingest → IWXXM gate | Implemented |
| F9 | Value-aware live decode + plain-language summary | Done (Code names dictionary deepen) |
| F10 | Workbench preview clarity (IWXXM pane + lint UX) | Done |
| F11 | Validation stack perf + msgspec HTTP + XSD codegen | Implemented |
| F12 | Publishable TAC product validation (`tac-validate`) | Implemented |
| F13 | Fast IWXXM validate (Rust + Schematron + PyPI) | Implemented |
| F14 | Publish `tac2iwxxm` + validate extras + PyPI/release CI | Implemented |
| F15 | TAC lint issue registry + METAR/SPECI quality bar | Done |
| F16 | Dissemination drawer + multi-DB upload (BYOC URI) | Done |
| F17 | WIS2 dissemination pathway | Done |
| F18 | EDIS → RTH Washington dissemination | Done |
| F19 | AMHS / SWIM / AFS adapters | Done |
| F20 | TAF + SPECI quality bar | Done |
| F21 | Public convert + optional Auth for long-term storage | Amended |
| F22 | Privacy preference center | Implemented |
| F23 | SIGMET family quality bar (general + VA) | Done |
| F24 | AIRMET quality bar | Done |
| F25 | WMO official example parity + UI gate | Done |
| F26 | VAA quality bar | Done |
| F27 | TCA quality bar | Done |
| F28 | SWXA quality bar | Done |
| F29 | Parameterized lint/convert/validate rule matrices | Done |
| F30 | Platform independence (Auth / DO DB / DOKS) | Done |
| F31 | Hybrid operator sessions (guest local + Auth long-term) | Done |
| F32 | VONA quality bar | Done |
| F33 | Secure mass file/folder ingest | Implemented |
| F34 | Contract + mutation quality gates | Done |
| F35 | Semantic vs exchange profiles | Implemented |
| F36 | National semantic + regional exchange profiles (incl. CA_ECCC; EV-077 VAA validate-first) | In progress |
| F37 | Live TAC map on Live map page | In progress |
| F39 | Station health dashboard (availability + quality grades) | In progress |
| M1 | Monorepo layout (`apps/` + `packages/` + `vendor/`) | Implemented |
| M2 | Vendor snapshot sync (wmo-im iwxxm-*) | Planned |
| M3 | GIFTs as in-repo package | Deprecated |
| M4 | Auth library in backend API | Implemented |
| M5 | Workspace tooling (uv + pnpm + Makefile) | Planned |
| M6 | Vendor upstream sync | Planned |

**Status key:** Implemented = production-ready; In progress = partial delivery;
Planned = approved; Superseded / Deprecated = replaced.

## Parity check protocol

When a skill says “check corpus parity” or “spec conformance”:

1. **Scope** — Does the change map to **product** (table above) and open tickets?
   If no → `[Scope Drift]`.
2. **Design** — Does behavior match **system-spec** + **api** (+ local **adr** if present)?
3. **Runtime** — Do names, URLs, and environment variables match **tech-spec** / **env**?
4. **Verification** — Are assertions grounded in **tests** and **journeys**?
5. **Decisions** — If code and corpus disagree, check local **decisions/** + **adr/**
   before you patch. Raise `[Contradiction]` / `[Ambiguity]`. Do not silently
   “fix around” the corpus.

Cite as: `[Corpus: <id>]` or `[Corpus: <path> §section]`.

## Folder layout

See [docs/README.md](docs/README.md). Runtime profiles live under
`config/deploy/profiles/`. Formatter and lint settings live under
`config/tooling/`. The SBOM lives under `config/sbom/`. Copy
`config/env.example` to `.env` for local secrets. Start the local stack with
`config/start-dev-servers.sh`. CI allowlists live under `scripts/ci/policy/`.
