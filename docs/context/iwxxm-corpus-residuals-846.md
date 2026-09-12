# Scoped context — IWXXM corpus residuals (#846 / S046)

**Status:** active  
**Session:** S046-iwxxm-corpus-residuals  
**Cycle:** EV-038  
**Epic:** [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846)

## Intent

Close residual children **#849–#861** left after S040/EV-032 (core epic children closed)
and S045/EV-037 (matrix disposition residuals closed).

## Authority sources

- Vendor pin + goldens / catalog — `[Corpus: tech-spec]` / `vendor/manifest.json`
- wmo-im/iwxxm, iwxxm-translation, iwxxm-codelists, codes.wmo.int, iwxxm-modelling
- Gap index: `docs/sessions/S040-iwxxm-corpus-quality/reports/t0.2-gap-index.md`
- Release-line: `docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md`

## Ticket groups

| Group | Issues | Risk |
|-------|--------|------|
| VONA deepen | #849, #850 | Encode; need WMO peer or cite-only defer |
| Release-line | #851–#855 | Automation + #854 UI |
| Corpus G3–G8 | #856–#861 | Mix of encode equality, docs OOS, CI drift |

## Non-goals

Metrics UI (#836), workbench epic (#840), hand-edit vendor schemas, full re-pin as primary goal.

## Corpus cites

`[Corpus: product]` · `[Corpus: system-spec]` · `[Corpus: tech-spec]` · `[Corpus: tests]` ·
`[Corpus: decisions]` · `[docs/domain/rules/COVERAGE_MATRIX.md]` ·
`[docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md]`
