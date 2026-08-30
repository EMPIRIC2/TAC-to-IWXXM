# Profile source catalog (semantic + exchange)

> **Corpus id**: `domain-profiles` ([CORPUS.md](../../CORPUS.md))  
> **Status**: P0/P1 catalog landed (EV-063 M5 / #913 — deepen continues in mining notes)  
> **Epic**: [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912)  
> **ADR**: [ADR-036](../adr/ADR-036-semantic-vs-exchange-profiles.md) (Accepted)

Authoritative-source catalog for **semantic** (TAC→IWXXM) and **exchange** (routing/packaging)
profiles. This directory is the standing SoT for profile *evidence*; implementation lives in
`packages/tac2iwxxm`, `packages/dissemination`, and national fixture trees.

## Scope

| Kind | Examples | Owns |
|------|----------|------|
| **Semantic** | `ICAO_2025`, `US_FAA_NWS`, `CA_ECCC`, `AU_BOM`, `NZ_CAA_MET`, thin/compat (#920) | TAC parse rules, RMK policy, national IWXXM extensions |
| **Exchange** | `GLOBAL_AFS`, `APAC_ROBEX`, `EUR_RODEX`, `AFI`, `CAR_SAM` | Bulletin/filename/routing packaging — **not** TAC grammar |

**Not here:** F16–F19 dissemination **destination** credentials (memory-only BYOC).

## Catalog layout (target)

```
profiles/
  README.md                      # this file
  NATIONAL_PROFILE_PLAYBOOK.md   # onboarding playbook (#1044 / EV-088)
  _template/                     # copy stubs for new nationals
  catalog.yaml                   # machine index (URLs, gaps, priority)
  semantic/
    ICAO_2025.md                 # P0 implemented
    US_FAA_NWS.md                # P0 implemented (#919 deepen)
    CA_ECCC.md                   # P1 implemented (#916) — reference impl
    AU_BOM.md / NZ_CAA_MET.md    # P1 thin kickoff (EV-087)
    UK_METOFFICE.md … HK_HKO.md  # P2 thin/compat (#920 / EV-089)
    ...
  exchange/
    GLOBAL_AFS.md                # P0 implemented (EV-065 / #921)
    APAC_ROBEX.md … CAR_SAM.md   # P2 stubs (EV-065/086)
    ...
```

**New national?** Start with [NATIONAL_PROFILE_PLAYBOOK.md](NATIONAL_PROFILE_PLAYBOOK.md)
and [`_template/`](_template/).

Fixture goldens (implementation): `profiles/<id>/<product>/{valid,invalid,expected-*}` under
package test trees — land with first heavy national profile (F36).

## Relationship to `docs/domain/mining/`

Mining notes under [`../mining/`](../mining/) are **transitory** working extracts. Promote
durable profile citations into this catalog (or linked domain rules docs) when #913 closes a
source row. Do not treat mining notes alone as profile SoT.

## Initial canonical map (F35)

| Canonical semantic ID | Legacy alias (until #1025) | Primary sources (starter) |
|-----------------------|----------------------------|---------------------------|
| `ICAO_2025` | `annex3` | ICAO Annex 3; WMO IWXXM 2025-2; PANS-MET |
| `US_FAA_NWS` | `iwxxm_us` | IWXXM-US; FMH-1; NWS schemas pin |

Exchange default: `GLOBAL_AFS` — see [`exchange/GLOBAL_AFS.md`](exchange/GLOBAL_AFS.md).

## Catalog index

Machine-readable index: [`catalog.yaml`](catalog.yaml) — P0/P1 profile rows with source URLs,
access tier, vendor pins, gaps, and mining-note cross-refs.

| Priority | Semantic | Exchange |
|----------|----------|----------|
| **P0** | `ICAO_2025`, `US_FAA_NWS` | `GLOBAL_AFS` (default) |
| **P1** | `CA_ECCC`, `AU_BOM`, `NZ_CAA_MET` | — |
| **P2** | `UK_METOFFICE`, `BR_DECEA`, `KR_KMA`, `JP_JMA`, `IN_IMD`, `HK_HKO` (#920) | `APAC_ROBEX`, `EUR_RODEX`, `AFI`, `CAR_SAM` |

## Open gaps (#913 deepen)

- [x] `catalog.yaml` with URL + access tier + gap status per profile id  
- [x] Semantic stubs for `ICAO_2025`, `US_FAA_NWS`, `CA_ECCC`  
- [ ] CA MANOBS/MANAIR section-level rule stubs for `CA_ECCC` (#916 / EV-064 in progress)  
- [x] AU TAF INTER/TAF3/RMK T/Q refs for `AU_BOM` (EV-087 mining kickoff)  
- [x] NZ domestic vs international TAF refs for `NZ_CAA_MET` (EV-087 mining kickoff)  
- [x] Thin/compat catalog + stubs for #920 ids (EV-089 Spec; Build fixtures/registry pending)  
- [ ] Regional exchange rule sources for ROBEX/RODEX variants (P2)

## References

- [NATIONAL_PROFILE_PLAYBOOK.md](NATIONAL_PROFILE_PLAYBOOK.md) — [#1044](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1044)
- [GAMET-spike.md](GAMET-spike.md) — EV-089 parse-only disposition
- [ADR-036](../../adr/ADR-036-semantic-vs-exchange-profiles.md)
- [#913 Mine ticket](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/913)
- [#1025 Alias cutover](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025)
