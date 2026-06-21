# ADR-008: F3 Airport Data UI Exposure (Stage 11)

**Status**: Accepted  
**Date**: 2026-06-20  
**Stage**: 11-verify-impl

## Context

During implementation verification, F3 (Airport Data Services) was flagged for fuller UI
exposure. The feature matrix marked Web UI as "Partial" — ICAO autocomplete used static
local data only, without surfacing backend airport-region lookup.

REQ-016 normally excludes product feature rewrites during migration; user explicitly approved
implementing F3 UI exposure during stage 11 verification.

## Decision

Add `AirportDetailsCard` to the conversion UI (`FileConverter`) showing:

- Airport name, city, country from local curated dataset
- ICAO region from `GET /api/v1/translation/airport-region/{icao}`

## Consequences

- F3 Web UI coverage improved without changing conversion logic
- New frontend API client function `fetchAirportRegion`
- Feature matrix should be updated post-merge to reflect partial → yes for Web UI
