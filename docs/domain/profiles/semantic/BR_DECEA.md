# BR_DECEA — Brazil DECEA thin overlay (P2)

> **Profile id**: `BR_DECEA` · **Kind**: semantic · **Priority**: P2 · **Status**: in_progress (EV-089 / [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920))  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **Path**: thin · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Brazil DECEA/ANAC semantic overlay extending `ICAO_2025` for METAR/SPECI/TAF/SIGMET/AIRMET.
SAM regional exchange packaging is **noted** only — deepen stays on [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921).
GAMET: **parse-only** fixtures; no IWXXM emit (see [GAMET-spike.md](../GAMET-spike.md)).

## Owns (target)

| Area | Scope |
|------|-------|
| TAC parse / normalize | ICAO baseline + BR corpora |
| IWXXM encode | **Core WMO only** |
| Products (convert) | METAR, SPECI, TAF, SIGMET, AIRMET |
| GAMET | Fixtures / archival parse only — **not** convert allowlist |
| Exchange | Pointer to `CAR_SAM` / #921 — no packaging code here |

## Standards hierarchy (L0–L6)

| Level | Source | Status |
|-------|--------|--------|
| L0 | DECEA / ANAC / AISWEB AIP | kickoff |
| L1–L3 | via ICAO_2025 | baseline |
| L4–L5 | National XSD / vocab | **N/A** |
| L6 | OGIMET / AISWEB ops | Build |

## Gaps

- [ ] Registry + allowlist for convert products
- [ ] GAMET TAC fixtures (parse-only)
- [ ] Durable AIP section cites after harvest

## References

- Mining: [`br-decea-tac-mining-notes.md`](../../mining/br-decea-tac-mining-notes.md)
- GAMET: [GAMET-spike.md](../GAMET-spike.md)
