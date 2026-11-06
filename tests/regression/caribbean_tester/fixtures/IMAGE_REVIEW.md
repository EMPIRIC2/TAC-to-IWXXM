# Image review — Caribbean tester screenshots

Opened with vision Read on every file under Downloads (65 total). Jamaica PNGs also copied under `fixtures/images/jamaica/` (2.3MB). Guyana JPEGs stay on Downloads only (too large for git).

## Jamaica (15)

| File | Visible TAC / UI | Coverage |
|------|------------------|----------|
| T011-a/b | TTPP VCSH as residual; soft Passed; INVALID_WEATHER VCSH | decode + lint + soft honesty |
| Recommended_UX_Mockup | Status-first result cards | resultCard |
| T146-a/b | TRPG `27/` incomplete dewpoint; soft not for publish | fail-closed + soft honesty |
| T302-a/b | MKJP `//// //////`; MISSING_VISIBILITY on old build | mkjp lint/convert |
| T360-a/b | SPECI MWCR TS/VCSH INVALID_WEATHER | SPECI lint/decode |
| T571-a/b | SIGMET CNL; isCancelReport | SIGMET CNL |
| T1059/T1060 a/b | MKJP AMD NOT SKED multiline; soft partial | AMD NOT SKED + multiline |

## Guyana (50)

Recurring themes across T012–T049 A/B pairs:

- VCSH / VCTS / TS flagged INVALID_WEATHER (fixed by lint locks)
- Soft preview Passed with residuals (fixed by soft honesty)
- AHL `SAGY31` with SPECI product → invalid heading (TT mismatch)
- SIGMET AHL “No TAC reports found after heading” on CNL/VA pastes
- TAF change groups PROB/TEMPO/BECMG; AMD NOT SKED / missing validity
- GTS peel + VRB knots on SYCJ METARs
- Older builds showed EV-048 in operator UI (forbidden now)

Class coverage: cross-product matrix, interop policies, harvest locks, raw TAC/XML, fuzz.

## Access proof

- DOCX: St Maarten + TT questionnaires readable (VCSH/lowest vis findings quoted in session)
- XLSX: Jamaica 149 TAC-like rows; TT 5; St Kitts 56; Guyana 49; Belize 4
- Images: 65/65 opened
