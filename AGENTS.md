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

| ID | Role | Path | Skills use it to… |
|----|------|------|-------------------|
| **product** | Approved features and acceptance | This file §Product feature index | Scope (feature `F*` / milestone `M*`); reject out-of-list work |
| **journeys** | End-user journeys | [docs/user-journeys.md](docs/user-journeys.md) | End-to-end / verify-impl sign-off (`UJ-*`) |
| **ui-style** | Living operator UI style guide | [docs/ui-style-guide.md](docs/ui-style-guide.md) | UI/UX tweak norms; cite when polishing the frontend |
| **system-spec** | Architecture, components, constraints | [docs/spec.md](docs/spec.md) | Design parity vs `apps/` + `packages/` + `vendor/` |
| **tech-spec** | Runtime / config / deploy / deps hub | [docs/tech-spec.md](docs/tech-spec.md) | Config names, environment, deploy topology, dependency pins |
| **api** | HTTP contract | [docs/api-contract.md](docs/api-contract.md) + [api/openapi.json](api/openapi.json) | Request / response / error shapes |
| **tests** | Test matrix and gates | [docs/test-plan.md](docs/test-plan.md) | Parity checks, smoke test-case IDs, CI expectations |
| **deps** | Live dependency inventory | [sbom/cyclonedx.json](sbom/cyclonedx.json) | Allowed packages; regenerate with `make sbom` |
| **env** | Environment variable names | [docs/env-variable.md](docs/env-variable.md) | Env var contract by layer |
| **changelog** | Release notes | [CHANGELOG.md](CHANGELOG.md) | Release history |

### Tech-spec satellites

| Path | Topic |
|------|--------|
| [docs/env-variable.md](docs/env-variable.md) | Environment variable contract |
| [deploy/profiles/](deploy/profiles/) | Non-secret runtime JSON (`local` / `staging` / `prod` / `e2e`) |
| [deploy/doks/](deploy/doks/) | DOKS deploy manifests and operator notes |
| [sbom/cyclonedx.json](sbom/cyclonedx.json) | CycloneDX SBOM (CI drift-checked on push) |

## Local opt-in (not in git; keep local copies)

These paths stay on the developer machine. Clones do not receive them.

| Path | When |
|------|------|
| `docs/adr/` | Architecture decisions (`ADR-NNN`) |
| `docs/decisions/` | Interview / evolve decision logs |
| `docs/engineering/` | NOW index, docstring bar, package DX |
| `docs/domain/`, `docs/guides/`, `docs/ops/`, `docs/integration/`, `docs/policies/` | Domain and runbooks |
| `docs/bug-reports/`, `docs/context/`, `docs/ui-ux-tweaks/`, `docs/assets/`, `docs/ste/` | Hotfix, context dumps, UX logs, STE dictionary |

## Product feature index

| # | Feature | Status |
|---|---------|--------|
| F1 | METAR → IWXXM conversion (GIFTs-era UX) | Superseded by F6 |
| F2 | IWXXM validation | Implemented |
| F3 | Airport data services | Implemented |
| F4 | IWXXM version handling | Implemented |
| F5 | User METAR work history | Implemented |
| F6 | General TAC→IWXXM (`tac2iwxxm`) | Implemented |
| F7 | Multi-product TAC operator UI / sessions | Implemented |
| F8 | Near-realtime TAC ingest → IWXXM gate | Implemented |
| F9 | Value-aware live decode + plain-language summary | Done |
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
| F36 | National semantic + regional exchange profiles | In progress |
| F37 | Live TAC map on Decode visuals | In progress |
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
`deploy/profiles/`. CI allowlists live under `scripts/ci/policy/`.
