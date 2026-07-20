# TAC lint issue catalog

> **Source**: generated from tac_validate.issue_registry  
> **Generated**: 2026-07-20 via `make catalog-regen`  
> **ADR**: ADR-028 / F15 / EV-011

Public `code` values are stable. Default severities may tighten in minor releases.
Do not invent ad-hoc `severity=` literals in rule bodies — import from the registry.

| Code | Severity | Message template | Product | Tags |
|------|----------|------------------|---------|------|
| `CLOUD_CB_OR_TCU` | `info` | {product} cloud group includes convective type CB/TCU | — | cloud, metar, speci, r4, cb, tcu |
| `EMPTY_TAC` | `error` | TAC text is empty | — | parse_gate, body |
| `INVALID_CLOUD_TOKEN` | `error` | {product} invalid cloud/VV token {token!r} — A3-2 #9 | — | cloud, metar, speci, r4 |
| `INVALID_CNL_SHAPE` | `error` | TAF CNL must end the message — A5-1 #6 | taf | cnl, taf |
| `INVALID_VISIBILITY` | `error` | {product} invalid visibility token (use SM, meters, or CAVOK) | — | visibility, metar, speci, r2 |
| `INVALID_WEATHER` | `error` | {product} invalid present weather token {token!r} — A3-2 #8 | — | weather, metar, speci, r3 |
| `MISSING_CCCC` | `error` | {product} missing ICAO location (CCCC) | — | station, metar, speci, taf |
| `MISSING_DTG` | `error` | {product} missing DTG: template field | — | dtg, vaa, tca |
| `MISSING_ISSUE_TIME` | `error` | TAF missing issue time ddhhmmZ — A5-1 #3 | taf | time, taf |
| `MISSING_MAX_WIND` | `error` | TCA missing MAX WIND: template field — A2-2 | tca | max_wind, tca |
| `MISSING_OBS_TIME` | `error` | {product} missing observation time ddhhmmZ — A3-2 #3 | — | time, metar, speci |
| `MISSING_PRODUCT_KEYWORD` | `error` | {product} TAC must contain one of {keywords} | — | parse_gate, header |
| `MISSING_QNH` | `error` | {product} missing QNH/altimeter (Qnnnn/Annnn) — A3-2 #11 | — | pressure, metar, speci |
| `MISSING_TEMP_DEWPOINT` | `error` | {product} missing temperature/dewpoint tt/td — A3-2 #10 | — | temperature, metar, speci |
| `MISSING_TERMINATOR` | `info` | Reports in bulletins end with '=' — add it before publishing | — | terminator, metar, speci, taf |
| `MISSING_VAAC` | `error` | VAA missing VAAC: template field — A2-1 | vaa | vaac, vaa |
| `MISSING_VALID` | `error` | {product} missing VALID ddhhmm/ddhhmm period — A6 identity | — | valid, sigmet, airmet |
| `MISSING_VALIDITY` | `error` | TAF missing validity period ddhh/ddhh — A5-1 #5 | taf | validity, taf |
| `MISSING_VISIBILITY` | `error` | {product} missing visibility or CAVOK — A3-2 #6 | — | visibility, metar, speci |
| `MISSING_WIND` | `error` | {product} missing surface wind group — A3-2 #5 | — | wind, metar, speci |
| `MULTIPLE_PHENOMENA` | `error` | {product} encodes multiple phenomenon families {hit} — A6 one-phenomenon gate | — | phenomenon, sigmet, airmet |
| `ODD_FIELD_ORDER` | `warning` | {product} groups out of A3-2 order (CCCC → ddhhmmZ → wind) | — | order, station, time, metar, speci, r1 |
| `UNKNOWN_PRODUCT` | `error` | Unknown product {product!r}; expected one of {expected} | — | parse_gate |
