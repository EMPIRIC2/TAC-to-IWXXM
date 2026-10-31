# US_MILITARY — United States military TAF lint

> **Profile id**: `US_MILITARY` · **Wire / lint id**: `us_military`  
> **Kind**: semantic · **Priority**: P2 · **Status**: implemented (EV-station-profile-tx-tn)  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Lint profile for US military TAFs that put TX/TN after BECMG/TEMPO/FM.
Convert uses core IWXXM (`annex3`). This is not `US_FAA_NWS` / `iwxxm_us`
(that pack forbids BECMG; military samples often use it).

## Owns

| Area | Scope |
|------|-------|
| Products | TAF |
| Lint | TX/TN after change groups → `TX_TN_PRESENT` (info), not `INVALID_TX_TN` |
| Stations | KBIX, KCVS, KGRK, KNID, KNYL, KPOE, KSZL (`UsMilitaryLintPolicy`) |
| IWXXM | Core annex3 emit only (no military XSD) |

## Observed in live TAC

| Signal | Notes |
|--------|-------|
| Trailing TX/TN | After BECMG/TEMPO/FM (e.g. KBIX, KCVS, KNYL) |
| Altimeter | `QNH####INS` on these bulletins |
| Tail remarks | e.g. `LAST NO AMDS` on some samples |

Annex 3 Table A5-1 places TX/TN on the base forecast. Use `ICAO_2025` / `annex3`
when you want that rule enforced as an error.

## Code

| Piece | Path |
|-------|------|
| Policy class | `packages/tac-validate/.../station_scoped_policy.py` → `UsMilitaryLintPolicy` |
| Lint catalog | `packages/tac-validate/.../lint_profiles.yaml` → `us_military` |
| T3 check | `packages/tac-validate/.../taf.py` (`accepts_end_tx_tn`) |
| Registry | `packages/tac2iwxxm/.../profile_registry.py` |

## Gaps

- Workbench does not auto-pick this profile from the station ICAO yet (`resolve_profile_for_station` exists)
- No FMH / military handbook mining beyond live TAC samples
