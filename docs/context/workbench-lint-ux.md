# Context — workbench lint UX (S048 / EV-040)

Scoped brief for deepen F7 / F10 / F15. [Corpus: product] [Corpus: api]

## Symptom / request

- Lint console truncates: `N issue(s): … (+M more)` — show each issue on its own line
- Preferences dialog is noisy — keep name + extension only
- Lint catalog should spell out official IWXXM/WMO/ICAO source attribution
- Add official IWXXM Collect + AHL bulletin examples
- NEW METAR → NEW TAC; action buttons above selects / bench
- Convert must not empty the INPUT field

## Example lint investigation (2026-08-06)

Product-aware `tac_validate.lint` on FE example bodies:

| Example | Result | Note |
|---------|--------|------|
| Most WMO TAC examples | PASS | info-only OK |
| `metar_a3_1.tac` | FAIL `INVALID_RVR` on `R12/1000U` | **False positive** — `_RVR_OK` omits tendency U/D |
| `metar_multi_ahl.txt` | FAIL `INVALID_VISIBILITY` on `121200` | **False positive** — AHL YYGGgg |

## Key code

- Truncation: `apps/frontend/src/hooks/useLiveWorkbenchAssist.ts`
- Clear on convert: `FileConverter.tsx` `setManualInput('')` on convert paths
- Actions: `data-testid="action-button-strip"`
- Prefs: `UserPreferencesDialog.tsx`
- Catalog: `issue_registry.py` + `GET /api/v1/lint-issue-catalog` + WorkbenchConsole
- Sources: `docs/domain/rules/RULE_SOURCE_URLS.md`, `PROVENANCE_MAP.json`
