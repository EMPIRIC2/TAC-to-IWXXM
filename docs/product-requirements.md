# Product requirements

> Index: [README.md](README.md)
> Last updated: 2026-11-13

This document defines the product and the behavioral requirements.
Technical pass criteria live in [technical-requirements.md](technical-requirements.md).
System shape lives in [architecture.md](architecture.md).

## Project definition

TAC to IWXXM converts aviation Traditional Alphanumeric Code (TAC) into
World Meteorological Organization (WMO) IWXXM XML.

Operators use a browser workbench to convert, lint, validate, decode, and
send messages. Integrators call the HTTP API. Maintainers ship Python packages
on PyPI.

The repository is one Git monorepo: `apps/` (deployable services), `packages/`
(libraries), and `vendor/` (read-only schema snapshots).

## Behavioral goals

1. An operator converts supported TAC products to IWXXM without a login.
2. An operator lints TAC and validates IWXXM output before dissemination.
3. An operator reads a plain-language decode of the TAC under edit.
4. A logged-in operator stores long-term work sessions in product Postgres.
5. A guest operator may keep short-term work in the browser when privacy
   settings allow it.
6. An operator sends output through dissemination adapters with one-shot
   credentials that stay in memory only.
7. A near-realtime worker ingests TAC, stores good results, and quarantines
   failures.
8. Continuous integration and live tests prove journeys in
   [user-journeys.csv](user-journeys.csv) through tests in
   [test-plan.csv](test-plan.csv).

## Non-goals

Do not add capabilities that [architecture.md](architecture.md) lists as
non-goals without a new planning cycle. Permanent exclusions include product
database use of Supabase PostgREST, in-app paste of Supabase auth keys for
dissemination, and automatic worker push to dissemination sinks.

## Capability index

Status values: Implemented, In progress, Planned, Superseded, Deprecated, Done.

| Capability                              | Status      | Acceptance (short)                                                                                                                                                                              |
| --------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Legacy METAR-only conversion UI         | Superseded  | Replaced by general TAC conversion                                                                                                                                                              |
| IWXXM validation                        | Implemented | Operator or API validates IWXXM with XSD and Schematron                                                                                                                                         |
| Airport data services                   | Implemented | Station and related lookups support convert and UI                                                                                                                                              |
| IWXXM version handling                  | Implemented | Operator selects a vendor-pinned IWXXM release line                                                                                                                                             |
| Work history                            | Implemented | Sessions persist for guests (local) and logged-in users (server)                                                                                                                                |
| General TAC to IWXXM conversion         | Implemented | Supported products convert through `tac2iwxxm`                                                                                                                                                  |
| Multi-product operator workbench        | Implemented | One workbench covers product entry and session flows; primary shell includes Convert, History, Rule catalogs, and Code names                                                                    |
| Near-realtime ingest worker             | Implemented | Worker stores or quarantines ingest results                                                                                                                                                     |
| Value-aware live decode                 | Done        | Decode shows values and a plain-language summary; Code names tab lists glossary codes tagged by product, country, and WMO amendment                                                             |
| Workbench IWXXM preview                 | Done        | Preview and soft-fail lint UX are clear                                                                                                                                                         |
| Validation stack performance            | Implemented | Fast HTTP encoding and validate path meet plan gates                                                                                                                                            |
| Publishable tac-validate package        | Implemented | Package installs from PyPI release tags                                                                                                                                                         |
| Fast iwxxm-validate package             | Implemented | Rust and Schematron path ships on PyPI                                                                                                                                                          |
| Publishable tac2iwxxm package           | Implemented | Package and extras ship with release CI                                                                                                                                                         |
| TAC lint registry for METAR and SPECI   | Done        | Catalogued issues drive the lint quality bar                                                                                                                                                    |
| Multi-database dissemination upload     | Done        | Bring-your-own-credentials URI upload works from the drawer                                                                                                                                     |
| WIS2 dissemination                      | Done        | WIS2 pathway works from the drawer                                                                                                                                                              |
| EDIS to RTH Washington dissemination    | Done        | EDIS pathway works from the drawer                                                                                                                                                              |
| AMHS, SWIM, and AFS dissemination       | Done        | Named adapters work from the drawer                                                                                                                                                             |
| Publishable iwxxm-dissemination package | In progress | Packaging and OIDC publish wiring for `packages/dissemination` as PyPI `iwxxm-dissemination` (import path `dissemination`); first tag `iwxxm-dissemination-v0.1.0`                              |
| TAF and SPECI quality bar               | Done        | Lint, convert, and validate goldens meet the bar                                                                                                                                                |
| Public convert with optional Auth       | Amended     | Convert stays public; Auth gates long-term storage                                                                                                                                              |
| Privacy preference center               | Implemented | Privacy controls gate local persistence                                                                                                                                                         |
| SIGMET family quality bar               | Done        | Ordinary and volcanic-ash SIGMET meet the bar                                                                                                                                                   |
| AIRMET quality bar                      | Done        | AIRMET meets the bar                                                                                                                                                                            |
| WMO example catalog and UI gate         | Done        | WMO-passing examples load in the UI and in CI                                                                                                                                                   |
| VAA quality bar                         | Done        | Volcanic ash advisory meets the bar                                                                                                                                                             |
| TCA quality bar                         | Done        | Tropical cyclone advisory meets the bar                                                                                                                                                         |
| SWXA quality bar                        | Done        | Space weather advisory meets the bar                                                                                                                                                            |
| Parameterized rule matrices             | Done        | Lint, convert, and validate matrices are parameterized                                                                                                                                          |
| Platform independence on DOKS           | Done        | DOKS, DigitalOcean Postgres, and Auth-only Supabase                                                                                                                                             |
| Hybrid operator sessions                | Done        | Guest local storage plus Auth long-term sessions                                                                                                                                                |
| VONA quality bar                        | Done        | Volcano notice meets the bar                                                                                                                                                                    |
| Secure mass file ingest                 | Implemented | Caps and content sniffing protect mass ingest                                                                                                                                                   |
| Contract and mutation quality gates     | Done        | Contract and mutation gates run in CI                                                                                                                                                           |
| Semantic vs exchange profiles           | Implemented | Profiles separate semantic content from exchange packaging                                                                                                                                      |
| National and regional profiles          | In progress | National semantic and regional exchange profiles                                                                                                                                                |
| Live TAC map on Decode                  | In progress | Shell Live map full page is primary; Results Map tab stays an embedded twin; Active reports filter shows only reports with a validity period that covers now                                    |
| Station health dashboard                | In progress | Public station availability and quality grades over 6 hours, 1 day, and 1 month; product breakdown; extensible metrics registry (deepens airport data, ingest, TAC quality, and operator shell) |
| Monorepo layout                         | Implemented | `apps/`, `packages/`, and `vendor/`                                                                                                                                                             |
| Vendor snapshot sync                    | Planned     | Upstream IWXXM schema sync                                                                                                                                                                      |
| Legacy GIFTs in-repo package            | Deprecated  | Removed at general TAC conversion cutover                                                                                                                                                       |
| Auth library in the backend API         | Implemented | JWKS service library (`packages/auth`); FE-direct Supabase login                                                                                                                                |
| Workspace tooling                       | Planned     | uv, pnpm, and Makefile depth                                                                                                                                                                    |
| Vendor upstream sync process            | Planned     | Ongoing vendor sync process                                                                                                                                                                     |

## Journey linkage

Every active capability that operators touch must map to one or more rows in
[user-journeys.csv](user-journeys.csv). Each journey row must list test ids from
[test-plan.csv](test-plan.csv) or a concrete test path.

## Change rule

New behavioral scope needs a planning cycle and an update to this file.
Do not add a capability only in chat.
