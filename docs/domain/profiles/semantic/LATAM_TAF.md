# LATAM_TAF — Latin America TAF lint

> **Profile id**: `LATAM_TAF` · **Wire / lint id**: `latam_taf`  
> **Kind**: semantic · **Priority**: P2 · **Status**: implemented (EV-station-profile-tx-tn)  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Lint profile for Latin American TAFs that put TX/TN after FM/BECMG/TEMPO.
Convert uses core IWXXM (`annex3`). This is not `BR_DECEA`; the stations are in
Colombia, Ecuador, and Venezuela.

## Owns

| Area | Scope |
|------|-------|
| Products | TAF |
| Lint | TX/TN after change groups → `TX_TN_PRESENT` (info), not `INVALID_TX_TN` |
| Stations | SKBO, SEQM, SKBQ, SVMI (`LatAmTafLintPolicy`) |
| IWXXM | Core annex3 emit only |

## Observed in live TAC

| Signal | Notes |
|--------|-------|
| Trailing TX/TN | After FM/TEMPO/BECMG (e.g. SKBO `TX19/3119Z TN10/0110Z`) |

Annex 3 Table A5-1 places TX/TN on the base forecast. Use `ICAO_2025` / `annex3`
when you want that rule enforced as an error.

## Code

| Piece | Path |
|-------|------|
| Policy class | `packages/tac-validate/.../station_scoped_policy.py` → `LatAmTafLintPolicy` |
| Lint catalog | `packages/tac-validate/.../lint_profiles.yaml` → `latam_taf` |
| T3 check | `packages/tac-validate/.../taf.py` (`accepts_end_tx_tn`) |
| Registry | `packages/tac2iwxxm/.../profile_registry.py` |

## Gaps

- Workbench does not auto-pick this profile from the station ICAO yet (`resolve_profile_for_station` exists)
- No national handbook mining beyond live TAC samples
