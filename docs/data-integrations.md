# Data integrations

> Index: [README.md](README.md) 
> Last updated: 2026-11-10

This document lists external and internal data systems that the product uses.
Flow order lives in [data-flows.md](data-flows.md).

## Systems

| System | Direction | Data | Auth / control |
|--------|-----------|------|----------------|
| Supabase Auth | In | JWT claims (user id) | Publishable key in browser; secret on API for Auth routes |
| DigitalOcean Postgres | In/Out | Work sessions, worker store/quarantine, optional audit | `DATABASE_URL` |
| Vendor schema snapshots | In | XSD, Schematron, codelists | Read-only files in git |
| Map providers | In | Map context for Live map | Provider keys and attribution rules |
| Airport and station reference | In | ICAO coordinates and related lookup | `reference-lookup` package and configured sources |
| WIS2, EDIS, AMHS, AFS, and SQL sinks | Out | IWXXM or packaged payloads | Memory-only credentials plus egress allowlist |
| Near-realtime ingest source | In | TAC bulletins or files for the ingest worker | Worker service credentials |
| PyPI and GHCR | Out | Package and image artifacts | Release CI credentials |

## Rules

1. Do not use Supabase as the product database.
2. Do not persist dissemination credentials.
3. Do not fetch live WMO HTML membership in pull-request CI.
4. Record new integrations here and in [integration-contract.md](integration-contract.md)
 in the same change set.
