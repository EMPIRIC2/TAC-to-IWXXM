# ADR-051: Live OurAirports lookup with a checked-in fallback

> **Status**: Accepted
> **Date**: 2026-09-23
> **Deciders**: User (EV-1271)

[Corpus: product §F6] [Corpus: system-spec] [Corpus: adr]

## Context

Convert resolves a 3-letter VOR from `vor_reference_points.json`. On 2026-09-23, convective SIGMET text named SRQ, which is not in that table, and convert raised `UnknownVOR`. Hand-editing the table does not scale. The lookup must stay compatible: a known table point still resolves, a latitude/longitude SIGMET still converts, and a double miss still raises `UnknownVOR`.

## Decision

1. Add workspace package `packages/reference-lookup`. `tac2iwxxm` calls it. The package does not import FastAPI or Supabase.
2. The public source is OurAirports, public domain. `navaids.csv` answers 3-letter ids. `airports.csv` answers 4-letter ICAO ids, matched on the `ident` column. Coordinates are `latitude_deg` and `longitude_deg`.
3. Download each file once per process with `httpx==0.28.1` and keep the parsed maps in memory. Timeout is 10 seconds per file. There is no retry and no env setting.
4. Try the public source first. Any error, including not-found, a transport failure, a parse failure, an empty coordinate, or more than one matching row, falls back to the checked-in table. Do not pick among matching rows.
5. If the table also misses, raise the existing `UnknownVOR`. Do not invent a coordinate.
6. Unit tests inject a small committed fixture. They do not call the network and they do not commit the full dump.

## Consequences

- The first lookup in a process can download about 14 MB. Later lookups in that process reuse the maps.
- A successful public hit wins even when the table has a different coordinate.
- Offline convert of a point that exists only in OurAirports fails with `UnknownVOR` after the download error, because the table is the fallback and it also misses.
- `httpx` is already in the lockfile at 0.28.1. The new package pins that exact version and the dependency inventory gains a row.

## Alternatives considered

- Keep extending the JSON table by hand. Rejected: that is the failure this decision describes.
- Put the client inside `tac2iwxxm`. Rejected: the lookup is its own package.
- `urllib` with no new dependency. Rejected: the client is `httpx`.
- Download on every lookup. Rejected: the maps are cached for the process.
- Vendor the full CSV in git. Rejected: tests keep a small fixture instead.
