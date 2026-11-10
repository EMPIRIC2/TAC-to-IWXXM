# Data flows

> Index: [README.md](README.md) 
> Last updated: 2026-11-10

This document describes the main data paths through the system.
Integration endpoints live in [data-integrations.md](data-integrations.md).

## Operator convert path

1. The browser sends TAC text to the API convert route.
2. The API calls `tac2iwxxm` and related packages with the selected product,
 profile, and IWXXM pin.
3. The API returns IWXXM XML and related metadata to the browser.
4. Optional lint and validate calls use `tac-validate` and `iwxxm-validate`.

No JWT is required on this path.

## Decode path

1. The browser sends TAC to the decode route while the operator types.
2. The API uses the `tac-decoding` package to return spans, values, and a
 plain-language summary.
3. The UI renders Code and Explanation panes. Map visuals may join reference
 data when the live TAC map capability is active.

## Session path

1. Guest mode may write short-term session state to IndexedDB when privacy
 settings allow it.
2. Logged-in mode writes long-term sessions to DigitalOcean Postgres through
 `/api/v1/work-sessions*` with a Bearer JWT.
3. Session rows store operator work state. They must not store dissemination
 credentials.

## Ingest path

1. The worker polls the configured ingest source.
2. The worker converts and validates through packages.
3. Good results store in product Postgres. Failures go to quarantine.
4. The worker does not disseminate.

## Dissemination path

1. The operator selects a sink and pastes one-shot credentials in the UI.
2. The browser posts the payload and credentials to the API.
3. The API checks the egress allowlist and SSRF rules.
4. The API sends through `packages/dissemination` and returns the result.
5. Credentials leave memory when the request ends.

## Schema path

1. Convert and validate read pins from `vendor/manifest.json`.
2. Schema files under `vendor/schemas/` stay read-only in normal development.
3. Vendor sync pull requests refresh snapshots. Hand edits are forbidden.
