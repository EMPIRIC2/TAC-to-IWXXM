# Provenance gaps — S045 / EV-037

**Date:** 2026-08-05  
**Cycle:** EV-037 · Session: S045-matrix-disposition-residuals  
**Prior:** S043 / EV-035 remine residuals #869 / #870 / #872

## Open `gap` rows

**None.** `PROVENANCE_MAP.json` `gaps[]` is empty after EV-037 dispositions.

## Disposed (no longer `gap`)

| Id | Prior | EV-037 disposition | Ticket |
|----|-------|--------------------|--------|
| `VONA_GUIDANCE_SILENT` | gap | **N/A** — upstream Guidance silence; encode SoT defined; non-blocking | #869 |
| `US_SCH_ABSENT` | gap | **N/A** — official US Schematron not published | #870 |
| `VONA/conversion` matrix | warn + ticket | warn retained (Guidance ⚠) with SoT hierarchy note | #869 |
| `METAR_US/iwxxm-validation` | warn | **ok** — WMO XSD/SCH + US XSD; US SCH N/A separately | #870 |
| Bulletin AHL source cells | stale `gap` in eight-family table | **AHL source = ✅** all families; impl columns separate | #872 |

## Residual implementation (not provenance `gap`)

Tracked in `COVERAGE_MATRIX` eight-family **impl** columns (body splitter / fixtures /
COLLECT deepen). Open GitHub children only for true parser/splitter/fixture/CI work —
not for source-document availability.
