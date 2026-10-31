# US_MILITARY — United States military TAF lint overlay

> **Profile id**: `US_MILITARY` · **Wire / lint id**: `us_military`  
> **Kind**: semantic · **Priority**: P2 · **Status**: implemented (EV-us-military-taf-tx-tn)  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Lint overlay for US military aerodrome TAFs that place TX/TN after BECMG/TEMPO (and related
change groups). Convert stays core IWXXM (`annex3` emit). This is not `US_FAA_NWS` /
`iwxxm_us`: that pack forbids BECMG, which military samples commonly use.

## Owns

| Area | Scope |
|------|-------|
| Products | **TAF** (lint overlay) |
| Lint | End-of-TAF TX/TN after change groups → `TX_TN_PRESENT` (info), not `INVALID_TX_TN` |
| IWXXM | Core annex3 emit only — no military XSD |

## Authoritative practice (observed)

| Signal | Notes |
|--------|-------|
| Trailing TX/TN | After BECMG/TEMPO chains (e.g. KBIX, KDOV, KCVS) |
| Altimeter form | `QNH####INS` common on these bulletins |

Annex 3 Table A5-1 still describes TX/TN on the base forecast. Operators who want that
strictness keep `ICAO_2025` / `annex3`.

## Implementation

| Component | Location |
|-----------|----------|
| Lint catalog | `packages/tac-validate/.../lint_profiles.yaml` → `us_military` |
| T3 gate | `packages/tac-validate/.../taf.py` `_check_taf_t3_elements` |
| Registry | `packages/tac2iwxxm/.../profile_registry.py` (`us_military` → emit `us_military` / annex3 plugin) |

## Gaps

- Auto-select from ICAO or `QNH####INS` (operators pick the profile today)
- LatAm end TX/TN under annex3 (unchanged)
- Mining notes / FMH-1 military cross-walk beyond live TAC samples
