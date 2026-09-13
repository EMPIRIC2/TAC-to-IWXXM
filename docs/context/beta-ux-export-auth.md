# Scoped context — beta UX + export/auth (EV-beta-ux-export-auth)

**Session:** EV-beta-ux-export-auth  
**Status:** active  
**Date:** 2026-09-11

## Intent

Operator trust pass: mark remaining maturing surfaces as beta; fix zip collision; clean
operator-visible validation copy and log severity chrome; collapsible Results; restore
register; verify export/import + auth.

## Primary surfaces

| Area | Paths |
|------|--------|
| Beta | `BetaBadge.tsx`, Dissemination*, `ConversionProfilePage`, `AppShellNav`, FileConverter toolbar |
| Zip | `FileConverter.handleDownloadAll`, `outputFilename.ts` |
| Lint copy | `packages/tac-validate/.../metar_speci.py`, `taf.py` |
| Log chrome | `ErrorLogPanel.tsx` |
| Deprecation | `tac2iwxxm/convert.py` `DEPRECATED_PROFILE_ALIAS` |
| Results | `FileConverter.tsx` Results region |
| Auth | `packages/auth` router + proxy; FE `Register.tsx` / `Login.tsx` |

## Corpus

[Corpus: product §F7 §F10 §F15 §F16–F19 §F31 §F35]  
[Corpus: journeys §UJ-001 §UJ-003]  
[Corpus: tests §TC-EV-beta-*]  
[Corpus: adr/ADR-043] [Corpus: adr/ADR-036]
