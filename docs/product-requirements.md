# Product requirements

> Index: [README.md](README.md)
> Last updated: 2026-11-24

This document defines the product and the behavioral requirements.
Technical pass criteria live in [technical-requirements.md](technical-requirements.md).
System shape lives in [architecture.md](architecture.md).

**Authoritative FR matrix for the open rebaseline:**
[functional-requirements.csv](functional-requirements.csv)
(session `EV-requirements-baseline-csv`, epic
[#1688](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1688)).
Where this file’s capability index disagrees with that CSV, the CSV wins until
Build deletes or rewrites the old code.

## Project definition

TAC to IWXXM converts aviation Traditional Alphanumeric Code (TAC) into
World Meteorological Organization (WMO) IWXXM XML.

Operators use a browser workbench to convert, lint, validate, and decode
messages, and to run live quality evaluation. Integrators call the HTTP API
with API keys. Maintainers ship Python packages on PyPI.

The repository is one Git monorepo: `apps/` (deployable services), `packages/`
(libraries), and `vendor/` (optional cache; official IWXXM XSD/Schematron are
fetched at build or runtime per FR-077).

## Behavioral goals

1. An operator converts supported products to IWXXM without a login (METAR,
   SPECI, TAF, AIRMET, SIGMET including VA/TC paths, VAA, TCA, SWXA, VONA,
   plus WAFS SIGWX and QVACI).
2. An operator lints TAC and validates IWXXM with official Schematron and
   matching XSD for the selected pin (`3.0`, `2021-2`, `2023-1`, `2025-2`).
3. An operator reads a plain-language decode of the product under edit.
4. Authenticated user history lives in Supabase (Auth + PostgREST). Shared and
   live-eval data live in DigitalOcean Postgres.
5. Privacy controls meet stated international compliance work (spike open).
6. Dissemination adapters are out of product scope for this rebaseline
   (deferred; code scheduled for delete).
7. A near-realtime worker ingests live files at 1000–5000 files in about one
   minute, with live eval queued ahead of local uploads.
8. Continuous integration and live tests prove journeys in
   [user-journeys.csv](user-journeys.csv) through tests in
   [test-plan.csv](test-plan.csv), with modes from
   [test-mode-matrix.csv](test-mode-matrix.csv) (many TCs to one journey).

## Non-goals

Deferred or removed for this rebaseline (see functional-requirements.csv drops
and epic #1688 children): dissemination drawer and sinks; national US/CA
profile extensions; LWIS/SAWR; G-AIRMET map layer; soft-fail IWXXM preview;
automatic IWXXM version migration; Render hosting; vendored schema trees as
source of truth.

## Capability index

Status values: Implemented, In progress, Planned, Superseded, Deprecated, Done.

| Capability                              | Status      | Acceptance (short)                                                                                                                                                                                                                                                                                                   |
| --------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Legacy METAR-only conversion UI         | Superseded  | Replaced by general TAC conversion                                                                                                                                                                                                                                                                                   |
| IWXXM validation                        | Implemented | Operator or API validates IWXXM with XSD and Schematron                                                                                                                                                                                                                                                              |
| Airport data services                   | Implemented | Station and related lookups support convert and UI                                                                                                                                                                                                                                                                   |
| IWXXM version handling                  | Implemented | Operator selects a vendor-pinned IWXXM release line                                                                                                                                                                                                                                                                  |
| Work history                            | Implemented | Sessions persist for guests (local) and logged-in users (server)                                                                                                                                                                                                                                                     |
| General TAC to IWXXM conversion         | Implemented | Supported products convert through `tac2iwxxm`                                                                                                                                                                                                                                                                       |
| Multi-product operator workbench        | Implemented | One workbench covers product entry and session flows; primary shell includes Convert, History, Rule catalogs, and Code names                                                                                                                                                                                         |
| Near-realtime ingest worker             | Implemented | Worker stores or quarantines ingest results                                                                                                                                                                                                                                                                          |
| Value-aware live decode                 | Done        | Decode shows values and a plain-language summary; Code names tab lists glossary codes tagged by product, country, and WMO amendment                                                                                                                                                                                  |
| Workbench IWXXM preview                 | Done        | Hard-convert IWXXM pane and lint UX; soft-preview toggle removed (FR-043)                                                                                                                                                                                                                                            |
| Validation stack performance            | Implemented | Fast HTTP encoding and validate path meet plan gates                                                                                                                                                                                                                                                                 |
| Publishable tac-validate package        | Implemented | Package installs from PyPI release tags                                                                                                                                                                                                                                                                              |
| Fast iwxxm-validate package             | Implemented | Rust and Schematron path ships on PyPI                                                                                                                                                                                                                                                                               |
| Publishable tac2iwxxm package           | Implemented | Package and extras ship with release CI                                                                                                                                                                                                                                                                              |
| TAC lint registry for METAR and SPECI | Done | Catalogued issues drive the lint quality bar; WMO handbook METAR/SPECI combination rules deepen group order, CAVOK, wind, visibility, RVR, weather, cloud, TREND, and remarks handling |
| Structured METAR/SPECI entry on Convert | Implemented | Operators can fill handbook group fields, insert TAC into the editor, and convert on the existing path |
| Optional omit of national remarks on convert | Implemented | Convert may drop remarks after RMK from IWXXM when the operator turns that option off |
| Multi-database dissemination upload     | Superseded  | Dropped for rebaseline (FR-052..056); HTTP/UI unmounted                                                                                                                                                                                                                                                              |
| WIS2 dissemination                      | Superseded  | Dropped for rebaseline (FR-052..056)                                                                                                                                                                                                                                                                                 |
| EDIS to RTH Washington dissemination    | Superseded  | Dropped for rebaseline (FR-052..056)                                                                                                                                                                                                                                                                                 |
| AMHS, SWIM, and AFS dissemination       | Superseded  | Dropped for rebaseline (FR-052..056)                                                                                                                                                                                                                                                                                 |
| Publishable iwxxm-dissemination package | In progress | Packaging and OIDC publish wiring for `packages/dissemination` as PyPI `iwxxm-dissemination` (import path `dissemination`); first tag `iwxxm-dissemination-v0.1.0`                                                                                                                                                   |
| TAF and SPECI quality bar               | Done        | Lint, convert, and validate goldens meet the bar                                                                                                                                                                                                                                                                     |
| Public convert with optional Auth       | Amended     | Convert stays public; Auth gates long-term storage                                                                                                                                                                                                                                                                   |
| Privacy preference center               | Implemented | Privacy controls gate local persistence                                                                                                                                                                                                                                                                              |
| SIGMET family quality bar               | Done        | Ordinary and volcanic-ash SIGMET meet the bar                                                                                                                                                                                                                                                                        |
| AIRMET quality bar                      | Done        | AIRMET meets the bar                                                                                                                                                                                                                                                                                                 |
| WMO example catalog and UI gate         | Done        | WMO-passing examples load in the UI and in CI                                                                                                                                                                                                                                                                        |
| VAA quality bar                         | Done        | Volcanic ash advisory meets the bar                                                                                                                                                                                                                                                                                  |
| TCA quality bar                         | Done        | Tropical cyclone advisory meets the bar                                                                                                                                                                                                                                                                              |
| SWXA quality bar                        | Done        | Space weather advisory meets the bar                                                                                                                                                                                                                                                                                 |
| Parameterized rule matrices             | Done        | Lint, convert, and validate matrices are parameterized                                                                                                                                                                                                                                                               |
| Platform independence on DOKS           | Done        | DOKS, DigitalOcean Postgres, and Auth-only Supabase                                                                                                                                                                                                                                                                  |
| Hybrid operator sessions                | Done        | Guest local storage plus Auth long-term sessions                                                                                                                                                                                                                                                                     |
| VONA quality bar                        | Done        | Volcano notice meets the bar                                                                                                                                                                                                                                                                                         |
| Secure mass file ingest                 | Implemented | Caps and content sniffing protect mass ingest                                                                                                                                                                                                                                                                        |
| Contract and mutation quality gates     | Done        | Contract and mutation gates run in CI                                                                                                                                                                                                                                                                                |
| Semantic vs exchange profiles           | Implemented | Profiles separate semantic content from exchange packaging                                                                                                                                                                                                                                                           |
| National and regional profiles          | In progress | National semantic and regional exchange profiles                                                                                                                                                                                                                                                                     |
| Live TAC map on Decode                  | In progress | Shell Live map full page is the only map home; Convert Results has no Map tab; Annex 3 / Overlays / Temperatures are mutually exclusive modes with a shared time-frame; overlays use a magnitude slider; temperatures support °C/°F; Active reports filter shows only reports with a validity period that covers now |
| Station health dashboard                | In progress | Public grades over 6h/1d/1mo/3mo from live stores; WMO region filter; maintenance and format counts; lint/validation issue counts; 90-day retention; Centennial proxies when data supports them (deepens airport data, ingest, TAC quality, and operator shell)                                                      |
| Monorepo layout                         | Implemented | `apps/`, `packages/`, and `vendor/`                                                                                                                                                                                                                                                                                  |
| Vendor snapshot sync                    | Planned     | Upstream IWXXM schema sync                                                                                                                                                                                                                                                                                           |
| Legacy GIFTs in-repo package            | Deprecated  | Removed at general TAC conversion cutover                                                                                                                                                                                                                                                                            |
| Auth library in the backend API         | Implemented | JWKS service library (`packages/auth`); FE-direct Supabase login                                                                                                                                                                                                                                                     |
| Workspace tooling                       | Planned     | uv, pnpm, and Makefile depth                                                                                                                                                                                                                                                                                         |
| Vendor upstream sync process            | Planned     | Ongoing vendor sync process                                                                                                                                                                                                                                                                                          |

## Journey linkage

Every active capability that operators touch must map to one or more rows in
[user-journeys.csv](user-journeys.csv). Each journey row must list test ids from
[test-plan.csv](test-plan.csv) or a concrete test path.

## Change rule

Update [functional-requirements.csv](functional-requirements.csv) when
behavioral scope changes, then reflect the delta here. Chat-only capabilities
are not accepted.

## Rebaseline note (EV-requirements-baseline-csv)

The capability index below still lists historical Implemented/Done rows. Rows
that conflict with the FR CSV (dissemination, national profiles, soft-preview,
guest IndexedDB as SoR, Auth-only Supabase) are **pending delete** under epic
[#1688](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1688). Do not treat
those index rows as the target state for new work.
