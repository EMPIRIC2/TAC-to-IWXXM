# TAC lint issue catalog

> **Source**: generated from tac_validate.issue_registry  
> **Generated**: 2026-07-22 via `make catalog-regen`  
> **ADR**: ADR-028 / F15 / EV-011

Public `code` values are stable. Default severities may tighten in minor releases.
Do not invent ad-hoc `severity=` literals in rule bodies — import from the registry.

| Code | Severity | Message template | Product | Tags |
|------|----------|------------------|---------|------|
| `AMD_PRESENT` | `info` | {product} AMD modifier present — research T1 / C1 | taf | modifier, taf, t1, c1 |
| `AT_PRESENT` | `info` | {product} AT time group present — research T2 | taf | change, taf, t2, at |
| `AUTO_PRESENT` | `info` | {product} AUTO modifier present — research R8 | — | modifier, metar, speci, r8 |
| `BECMG_PRESENT` | `info` | {product} BECMG change group present — research T2 | taf | change, taf, t2, becmg |
| `CAVOK_PRESENT` | `info` | {product} CAVOK present — research T3 / S1 | — | cavok, metar, speci, taf, t3, s1 |
| `CLOUD_CB_OR_TCU` | `info` | {product} cloud group includes convective type CB/TCU | — | cloud, metar, speci, r4, cb, tcu |
| `CNL_REPORT` | `info` | {product} CNL cancel report — research T1 | taf | cnl, taf, t1 |
| `COR_PRESENT` | `info` | {product} COR modifier present — research R8 / T1 / C1 | — | modifier, metar, speci, taf, r8, t1, c1 |
| `EMPTY_TAC` | `error` | TAC text is empty | — | parse_gate, body |
| `FM_PRESENT` | `info` | {product} FM change group present — research T2 | taf | change, taf, t2, fm |
| `INVALID_CLOUD_TOKEN` | `error` | {product} invalid cloud/VV token {token!r} — A3-2 #9 | — | cloud, metar, speci, r4 |
| `INVALID_CNL_SHAPE` | `error` | TAF CNL must end the message — A5-1 #6 | taf | cnl, taf, t1 |
| `INVALID_NIL` | `error` | {product} NIL must not include body groups — research R8 / T1 / C1 | — | nil, metar, speci, taf, r8, t1, c1 |
| `INVALID_PROB` | `error` | {product} invalid PROB (only 30|40; must not qualify BECMG/FM) — App 5 §1.4 / research T2 | taf | change, taf, t2, prob |
| `INVALID_REMARK` | `error` | {product} malformed remark group {token!r} | — | remark, metar, speci, r5, iwxxm_us |
| `INVALID_RVR` | `error` | {product} invalid RVR token {token!r} — research R8 | — | rvr, metar, speci, r8 |
| `INVALID_TX_TN` | `error` | {product} TX/TN allowed on base forecast only — research T3 | taf | temperature, taf, t3 |
| `INVALID_VISIBILITY` | `error` | {product} invalid visibility token (use SM, meters, or CAVOK) | — | visibility, metar, speci, r2 |
| `INVALID_WEATHER` | `error` | {product} invalid present weather token {token!r} — A3-2 #8 | — | weather, metar, speci, r3 |
| `INVALID_WIND` | `error` | {product} invalid wind token {token!r} — research R8 | — | wind, metar, speci, r8 |
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
| `MULTI_REPORT_BULLETIN` | `info` | {product} bulletin has multiple TAC reports — one IWXXM report per TAC (Guidance C1) | — | bulletin, metar, speci, taf, c1, one_report |
| `NCD_PRESENT` | `info` | {product} NCD present — research S1 | — | cloud, metar, speci, s1, auto |
| `NIL_REPORT` | `info` | {product} NIL report — research R8 / T1 / C1 | — | nil, metar, speci, taf, r8, t1, c1 |
| `NOSIG_PRESENT` | `info` | {product} NOSIG trend present — research R8 | — | trend, metar, speci, r8 |
| `NSC_PRESENT` | `info` | {product} NSC present — research T3 / S1 / C1 | — | cloud, metar, speci, taf, t3, s1, c1 |
| `NSW_PRESENT` | `info` | {product} NSW present — research T3 / S1 | — | weather, metar, speci, taf, t3, s1 |
| `ODD_FIELD_ORDER` | `warning` | {product} groups out of A3-2 order (CCCC → ddhhmmZ → wind) | — | order, station, time, metar, speci, r1 |
| `PROB_PRESENT` | `info` | {product} PROB30/40 change group present — research T2 | taf | change, taf, t2, prob |
| `REMARK_US_EXTENSION` | `info` | {product} US remarks present — iwxxm_us profile awareness | — | remark, metar, speci, r5, iwxxm_us |
| `RVR_PRESENT` | `info` | {product} RVR group present — research R8 | — | rvr, metar, speci, r8 |
| `TEMPO_PRESENT` | `info` | {product} TEMPO trend present — research R8 / T2 | — | trend, change, metar, speci, taf, r8, t2 |
| `TL_PRESENT` | `info` | {product} TL time group present — research T2 | taf | change, taf, t2, tl |
| `TX_TN_PRESENT` | `info` | {product} TX/TN temperature forecasts on base — research T3 | taf | temperature, taf, t3 |
| `UNKNOWN_PRODUCT` | `error` | Unknown product {product!r}; expected one of {expected} | — | parse_gate |
| `VV_NOT_OBSERVABLE` | `info` | {product} VV/// — verticalVisibility nil notObservable — research S1 | — | cloud, metar, speci, s1, vv |
| `VV_OMIT` | `info` | {product} VV/// — omit verticalVisibility without nilReason — research T3 | taf | cloud, taf, t3, vv |
| `WIND_DIR_VARIATION` | `info` | {product} wind direction variation dddVddd — research S1 | — | wind, metar, speci, s1 |
| `WIND_VRB_OR_GUST` | `info` | {product} wind uses VRB and/or gust — research R8 | — | wind, metar, speci, r8 |
| `WX_NOT_OBSERVABLE` | `info` | {product} present weather // — nil notObservable — research S1 | — | weather, metar, speci, s1 |
