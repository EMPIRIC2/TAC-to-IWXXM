"""Maintainable TAC lint issue registry (F15 / ADR-028).

Rules import ``IssueSpec`` rows via ``by_code`` / ``issue_from`` instead of inventing
severity or code string literals. Catalog export (``make catalog-regen``) iterates
``ISSUES``.
"""

from __future__ import annotations

import msgspec

from tac_validate.models import Issue


class IssueSpec(msgspec.Struct, frozen=True):
    """
    One registered lint issue definition.

    Parameters
    ----------
    code :
        Stable SCREAMING_SNAKE public id.
    severity :
        Default ``error``, ``warning``, or ``info``.
    message_template :
        Human message; may include ``str.format`` placeholders (e.g. ``{product}``).
    product :
        Optional product tag for catalog filtering (``None`` = shared / multi-product).
    tags :
        Optional catalog / FE tags (not part of the public code string).
    """

    code: str
    severity: str
    message_template: str
    product: str | None = None
    tags: tuple[str, ...] = ()


def _row(
    code: str,
    severity: str,
    message_template: str,
    *,
    product: str | None = None,
    tags: tuple[str, ...] = (),
) -> IssueSpec:
    return IssueSpec(
        code=code,
        severity=severity,
        message_template=message_template,
        product=product,
        tags=tags,
    )


# Seed: every code currently emitted by rules.py / product_rules.py (T1.2).
ISSUES: tuple[IssueSpec, ...] = (
    _row(
        "UNKNOWN_PRODUCT",
        "error",
        "Unknown product {product!r}; expected one of {expected}",
        tags=("parse_gate",),
    ),
    _row(
        "EMPTY_TAC",
        "error",
        "TAC text is empty",
        tags=("parse_gate", "body"),
    ),
    _row(
        "MISSING_PRODUCT_KEYWORD",
        "error",
        "{product} TAC must contain one of {keywords}",
        tags=("parse_gate", "header"),
    ),
    _row(
        "INVALID_AHL",
        "error",
        "WMO abbreviated heading is not valid communications format",
        tags=("bulletin", "ahl", "parse_gate"),
    ),
    _row(
        "MISSING_TERMINATOR",
        "info",
        "Reports in bulletins end with '=' - add it before publishing",
        tags=("terminator", "metar", "speci", "taf"),
    ),
    _row(
        "MISSING_CCCC",
        "error",
        "{product} missing ICAO location (CCCC)",
        tags=("station", "metar", "speci", "taf"),
    ),
    _row(
        "MISSING_OBS_TIME",
        "error",
        "{product} missing observation time ddhhmmZ - A3-2 #3",
        tags=("time", "metar", "speci"),
    ),
    _row(
        "ODD_FIELD_ORDER",
        "warning",
        "{product} groups out of A3-2 order (CCCC → ddhhmmZ → wind)",
        tags=("order", "station", "time", "metar", "speci", "r1"),
    ),
    _row(
        "MISSING_WIND",
        "error",
        "{product} missing surface wind group - A3-2 #5",
        tags=("wind", "metar", "speci"),
    ),
    _row(
        "MISSING_VISIBILITY",
        "error",
        "{product} missing visibility or CAVOK - A3-2 #6",
        tags=("visibility", "metar", "speci"),
    ),
    _row(
        "INVALID_VISIBILITY",
        "error",
        "{product} invalid visibility token (use SM, meters, or CAVOK)",
        tags=("visibility", "metar", "speci", "r2"),
    ),
    _row(
        "INVALID_WEATHER",
        "error",
        "{product} invalid present weather token {token!r} - A3-2 #8",
        tags=("weather", "metar", "speci", "r3"),
    ),
    _row(
        "MISSING_TEMP_DEWPOINT",
        "error",
        "{product} missing temperature/dewpoint tt/td - A3-2 #10",
        tags=("temperature", "metar", "speci"),
    ),
    _row(
        "MISSING_QNH",
        "error",
        "{product} missing QNH/altimeter (Qnnnn/Annnn) - A3-2 #11",
        tags=("pressure", "metar", "speci"),
    ),
    _row(
        "INVALID_CLOUD_TOKEN",
        "error",
        "{product} invalid cloud/VV token {token!r} - A3-2 #9",
        tags=("cloud", "metar", "speci", "r4"),
    ),
    _row(
        "CLOUD_CB_OR_TCU",
        "info",
        "{product} cloud group includes convective type CB/TCU",
        tags=("cloud", "metar", "speci", "r4", "cb", "tcu"),
    ),
    _row(
        "REMARK_US_EXTENSION",
        "info",
        "{product} US remarks present - iwxxm_us profile awareness",
        tags=("remark", "metar", "speci", "r5", "iwxxm_us"),
    ),
    _row(
        "INVALID_REMARK",
        "error",
        "{product} malformed remark group {token!r}",
        tags=("remark", "metar", "speci", "r5", "iwxxm_us"),
    ),
    _row(
        "AUTO_PRESENT",
        "info",
        "{product} includes the AUTO modifier, meaning the observation was produced by an automatic station. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 Table A3-2 / App 3. Full normative text may require purchase.",
        tags=("modifier", "metar", "speci", "r8"),
    ),
    _row(
        "CA_STATUTE_MILE_VIS",
        "info",
        "{product} uses statute-mile visibility - MANOBS Canadian overlay",
        tags=("visibility", "metar", "speci", "ca_eccc", "manobs"),
    ),
    _row(
        "CA_ALTIMETER_INHG",
        "info",
        "{product} uses inch-of-mercury altimeter (A####) - MANOBS Canadian overlay",
        tags=("pressure", "metar", "speci", "ca_eccc", "manobs"),
    ),
    _row(
        "CA_REMARK_MANOBS",
        "info",
        "{product} Canadian REMARKS present - ca_eccc profile awareness",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs"),
    ),
    _row(
        "CA_REMARK_PRESRR",
        "info",
        "{product} MANOBS pressure rising rapidly (PRESRR) - ca_eccc profile awareness",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs", "presrr"),
    ),
    _row(
        "CA_REMARK_PRESFR",
        "info",
        "{product} MANOBS pressure falling rapidly (PRESFR) - ca_eccc profile awareness",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs", "presfr"),
    ),
    _row(
        "CA_REMARK_NOSPECI",
        "info",
        "{product} MANOBS no-specials remark (NOSPECI) - ca_eccc profile awareness",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs", "nospeci"),
    ),
    _row(
        "CA_REMARK_SECTOR_VIS",
        "info",
        "{product} MANOBS sector visibility remark - ca_eccc profile awareness",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs", "visibility"),
    ),
    _row(
        "CA_ALTIMETER_NOT_OBS",
        "info",
        "{product} altimeter not observable (A////) - MANOBS Canadian overlay",
        tags=("pressure", "metar", "speci", "ca_eccc", "manobs"),
    ),
    _row(
        "CA_METAR_LWIS",
        "info",
        "{product} Limited Weather Information System (LWIS) report - MANOBS CA overlay",
        tags=("metar", "ca_eccc", "manobs", "lwis"),
    ),
    _row(
        "CA_METAR_SAWR",
        "info",
        "{product} Surface Aviation Weather Report (SAWR) - MANOBS CA overlay",
        tags=("metar", "ca_eccc", "manobs", "sawr"),
    ),
    _row(
        "CA_TAF_NCLWS",
        "info",
        "{product} includes MANAIR non-convective low-level wind shear (WS group)",
        tags=("taf", "ca_eccc", "manair", "nclws"),
    ),
    _row(
        "US_TAF_BECMG_FORBIDDEN",
        "error",
        "{product} BECMG change group is forbidden under US_FAA_NWS",
        product="TAF",
        tags=("taf", "iwxxm_us", "us_faa_nws"),
    ),
    _row(
        "US_TAF_TEMPO_MAX_4H",
        "error",
        "{product} TEMPO change group exceeds 4-hour US_FAA_NWS maximum",
        product="TAF",
        tags=("taf", "iwxxm_us", "us_faa_nws"),
    ),
    _row(
        "US_SWXA_SATCOM_NOT_ISSUED",
        "error",
        "{product} SATCOM space weather is not issued under US_FAA_NWS",
        product="SWXA",
        tags=("swxa", "iwxxm_us", "us_faa_nws", "satcom"),
    ),
    _row(
        "US_TCA_OBSERVED_CB_NOT_PROVIDED",
        "error",
        "{product} observed CB must be NIL under US_FAA_NWS - observed CB not provided",
        product="TCA",
        tags=("tca", "iwxxm_us", "us_faa_nws", "cb"),
    ),
    _row(
        "CA_AIRMET_GFA",
        "info",
        "{product} encodes MANAIR GFA compound phenomenon - ca_eccc profile awareness",
        tags=("airmet", "ca_eccc", "manair", "gfa"),
    ),
    _row(
        "COR_PRESENT",
        "info",
        "{product} includes the COR (correction) modifier, indicating a corrected report replacing a prior issue. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        tags=("modifier", "metar", "speci", "taf", "r8", "t1", "c1"),
    ),
    _row(
        "AMD_PRESENT",
        "info",
        "{product} includes the AMD (amendment) modifier, indicating an amended forecast. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("modifier", "taf", "t1", "c1"),
    ),
    _row(
        "NIL_REPORT",
        "info",
        "{product} is a NIL report (no observation/forecast available for the period). Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        tags=("nil", "metar", "speci", "taf", "r8", "t1", "c1"),
    ),
    _row(
        "CNL_REPORT",
        "info",
        "{product} is a CNL (cancel) report that withdraws a previously issued forecast. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("cnl", "taf", "t1"),
    ),
    _row(
        "INVALID_NIL",
        "error",
        "{product} NIL report also contains body groups; NIL must stand alone without observation/forecast body content. Error: the TAC does not meet a required format or product rule and should be corrected. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        tags=("nil", "metar", "speci", "taf", "r8", "t1", "c1"),
    ),
    _row(
        "MULTI_REPORT_BULLETIN",
        "info",
        "{product} bulletin has multiple TAC reports - one IWXXM report per TAC (Guidance C1)",
        tags=("bulletin", "metar", "speci", "taf", "sigmet", "airmet", "c1", "one_report"),
    ),
    _row(
        "NOSIG_PRESENT",
        "info",
        "{product} includes a NOSIG trend, meaning no significant change is expected. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 Table A3-2 / App 3. Full normative text may require purchase.",
        tags=("trend", "metar", "speci", "r8"),
    ),
    _row(
        "TEMPO_PRESENT",
        "info",
        "{product} includes a TEMPO trend/change group for temporary fluctuations. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        tags=("trend", "change", "metar", "speci", "taf", "r8", "t2"),
    ),
    _row(
        "RVR_PRESENT",
        "info",
        "{product} includes one or more runway visual range (RVR) groups. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 Table A3-2 / App 3. Full normative text may require purchase.",
        tags=("rvr", "metar", "speci", "r8"),
    ),
    _row(
        "INVALID_RVR",
        "error",
        "{product} has an invalid RVR token {token!r} that does not match allowed RVR syntax. Error: the TAC does not meet a required format or product rule and should be corrected. Source: No single RVR concept register - cite 49-2 family + grammar sources.",
        tags=("rvr", "metar", "speci", "r8"),
    ),
    _row(
        "WIND_VRB_OR_GUST",
        "info",
        "{product} wind group uses variable direction (VRB) and/or a gust value. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 Table A3-2 / App 3. Full normative text may require purchase.",
        tags=("wind", "metar", "speci", "r8"),
    ),
    _row(
        "INVALID_WIND",
        "error",
        "{product} has an invalid wind token {token!r}. Error: the TAC does not meet a required format or product rule and should be corrected. Source: Wind not in AerodromePresentWeather list.",
        tags=("wind", "metar", "speci", "r8"),
    ),
    _row(
        "MISSING_ISSUE_TIME",
        "error",
        "TAF missing issue time ddhhmmZ - A5-1 #3",
        product="taf",
        tags=("time", "taf"),
    ),
    _row(
        "MISSING_VALIDITY",
        "error",
        "TAF missing validity period ddhh/ddhh - A5-1 #5",
        product="taf",
        tags=("validity", "taf"),
    ),
    _row(
        "INVALID_CNL_SHAPE",
        "error",
        "TAF CNL must end the message - A5-1 #6",
        product="taf",
        tags=("cnl", "taf", "t1"),
    ),
    _row(
        "FM_PRESENT",
        "info",
        "{product} includes an FM (from) change group that starts a new forecast period. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("change", "taf", "t2", "fm"),
    ),
    _row(
        "BECMG_PRESENT",
        "info",
        "{product} includes a BECMG (becoming) change group describing a gradual change. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("change", "taf", "t2", "becmg"),
    ),
    _row(
        "PROB_PRESENT",
        "info",
        "{product} includes a PROB30 or PROB40 probability change group. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("change", "taf", "t2", "prob"),
    ),
    _row(
        "TL_PRESENT",
        "info",
        "{product} includes a TL (until) time qualifier on a change group. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("change", "taf", "t2", "tl"),
    ),
    _row(
        "AT_PRESENT",
        "info",
        "{product} includes an AT time qualifier on a change group. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("change", "taf", "t2", "at"),
    ),
    _row(
        "INVALID_PROB",
        "error",
        "{product} has an invalid PROB group (only PROB30/PROB40 are allowed; PROB must not qualify BECMG/FM). Error: the TAC does not meet a required format or product rule and should be corrected. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("change", "taf", "t2", "prob"),
    ),
    _row(
        "TX_TN_PRESENT",
        "info",
        "{product} includes TX/TN temperature forecast groups on the base forecast. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("temperature", "taf", "t3"),
    ),
    _row(
        "INVALID_TX_TN",
        "error",
        "{product} places TX/TN temperature groups outside the base forecast where they are not allowed. Error: the TAC does not meet a required format or product rule and should be corrected. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("temperature", "taf", "t3"),
    ),
    _row(
        "CAVOK_PRESENT",
        "info",
        "{product} includes CAVOK (ceiling and visibility OK). Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        tags=("cavok", "metar", "speci", "taf", "t3", "s1"),
    ),
    _row(
        "NSC_PRESENT",
        "info",
        "{product} includes NSC (no significant cloud). Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        tags=("cloud", "metar", "speci", "taf", "t3", "s1", "c1"),
    ),
    _row(
        "NSC_WITH_CLOUD_LAYERS",
        "warning",
        "{product} combines NSC (no significant cloud) with FEW/SCT/BKN/OVC cloud layers in the same group - FAQ §14.3 exclusivity. Warning: conflicting cloud amounts may confuse downstream systems; review before dissemination. Source: ICAO Annex 3 FAQ §14.3. Full normative text may require purchase.",
        tags=("cloud", "metar", "speci", "taf", "t3", "s1", "c1", "ev023"),
    ),
    _row(
        "NCD_PRESENT",
        "info",
        "{product} includes NCD (no cloud detected), typically from AUTO stations. Informational: noted for operator awareness; does not by itself block conversion. Source: NCD cloud amount notation family.",
        tags=("cloud", "metar", "speci", "s1", "auto"),
    ),
    _row(
        "NSW_PRESENT",
        "info",
        "{product} includes NSW (nil significant weather). Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        tags=("weather", "metar", "speci", "taf", "t3", "s1"),
    ),
    _row(
        "VV_OMIT",
        "info",
        "{product} uses VV///; vertical visibility should be omitted without a nil reason in this product context. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.",
        product="taf",
        tags=("cloud", "taf", "t3", "vv"),
    ),
    _row(
        "VV_NOT_OBSERVABLE",
        "info",
        "{product} uses VV/// meaning vertical visibility is not observable. Informational: noted for operator awareness; does not by itself block conversion. Source: Vertical visibility missingness via nil.",
        tags=("cloud", "metar", "speci", "s1", "vv"),
    ),
    _row(
        "WX_NOT_OBSERVABLE",
        "info",
        "{product} present weather uses // meaning weather phenomena are not observable. Informational: noted for operator awareness; does not by itself block conversion. Source: nilReason notObservable; prefer iwxxm/nil when pin policy says so.",
        tags=("weather", "metar", "speci", "s1"),
    ),
    _row(
        "WIND_DIR_VARIATION",
        "info",
        "{product} includes wind direction variation in dddVddd form. Informational: noted for operator awareness; does not by itself block conversion. Source: ICAO Annex 3 Table A3-2 / App 3. Full normative text may require purchase.",
        tags=("wind", "metar", "speci", "s1"),
    ),
    _row(
        "MISSING_VALID",
        "error",
        "{product} missing VALID ddhhmm/ddhhmm period - A6 identity",
        tags=("valid", "sigmet", "airmet"),
    ),
    _row(
        "MULTIPLE_PHENOMENA",
        "error",
        "{product} encodes multiple phenomenon families {hit} - A6 one-phenomenon gate",
        tags=("phenomenon", "sigmet", "airmet"),
    ),
    # S059 / EV-050 / #959 - offline WMO register membership (Validated)
    _row(
        "UNKNOWN_WMO_MEMBERSHIP",
        "error",
        "{product} token {token!r} not in WMO register ({family})",
        tags=("membership", "wmo", "ev050", "weather", "cloud", "phenomenon"),
    ),
    # F23 theme G1 - general SIGMET exceptional (#733 / research G1)
    _row(
        "SIGMET_CNL",
        "info",
        "SIGMET CNL cancel report. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("cnl", "sigmet", "g1", "c1"),
    ),
    _row(
        "STNR_MOVEMENT",
        "info",
        "SIGMET/AIRMET STNR stationary movement. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("stnr", "movement", "sigmet", "airmet", "g1", "c1", "a2"),
    ),
    _row(
        "POINT_LOCATION",
        "info",
        "SIGMET single-point location (encode CircleByCenterPoint r=0). Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("geometry", "point", "sigmet", "g1"),
    ),
    _row(
        "SINGLE_ALTITUDE",
        "info",
        "SIGMET single altitude (same lower/upper). Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("altitude", "sigmet", "g1"),
    ),
    _row(
        "POLYGON_LOCATION",
        "info",
        "SIGMET polygon/line WI geometry. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("geometry", "polygon", "sigmet", "g1"),
    ),
    _row(
        "TOP_ABV_OR_BLW",
        "info",
        "SIGMET/AIRMET TOP ABV/BLW level grammar. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("altitude", "top", "sigmet", "airmet", "g1", "a2"),
    ),
    _row(
        "INVALID_SIGMET_CNL",
        "error",
        "SIGMET CNL must omit phenomenon/analysis body. Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("cnl", "sigmet", "g1"),
    ),
    _row(
        "INVALID_SIGMET_COR",
        "error",
        "SIGMET must not use COR (cancel + re-issue). Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("cor", "sigmet", "g1", "c1"),
    ),
    _row(
        "INVALID_STNR_MOVEMENT",
        "error",
        "SIGMET/AIRMET STNR conflicts with MOV. Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("stnr", "movement", "sigmet", "airmet", "g1", "a2"),
    ),
    # F23 theme G2 - sequence / validity / FIR / OBS·FCST / intensity (#733)
    _row(
        "SIGMET_SEQUENCE",
        "info",
        "{product} includes a recognized SIGMET SEQUENCE element/group in the TAC text. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("sequence", "sigmet", "g2"),
    ),
    _row(
        "FIR_OR_CTA",
        "info",
        "SIGMET FIR/CTA/UIR airspace identity. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("fir", "cta", "sigmet", "g2"),
    ),
    _row(
        "OBS_OR_FCST",
        "info",
        "SIGMET/AIRMET OBS or FCST analysis. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("obs", "fcst", "sigmet", "airmet", "g2", "a2"),
    ),
    _row(
        "INTENSITY_CHANGE",
        "info",
        "SIGMET/AIRMET intensity change INTSF/WKN/NC. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("intensity", "sigmet", "airmet", "g2", "a2"),
    ),
    _row(
        "MISSING_SEQUENCE",
        "error",
        "SIGMET/AIRMET missing sequence number. Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("sequence", "sigmet", "airmet", "g2", "a1"),
    ),
    _row(
        "INVALID_VALIDITY_DURATION",
        "error",
        "SIGMET VALID period exceeds 4 hours (WS). Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("valid", "sigmet", "g2"),
    ),
    _row(
        "MISSING_FIR_OR_CTA",
        "error",
        "SIGMET/AIRMET missing FIR/CTA/UIR airspace identity. Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("fir", "cta", "sigmet", "airmet", "g2", "a1"),
    ),
    _row(
        "MISSING_OBS_OR_FCST",
        "error",
        "SIGMET/AIRMET missing OBS or FCST. Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("obs", "fcst", "sigmet", "airmet", "g2", "a2"),
    ),
    # F23 theme V1 - VA SIGMET (#739 / research V1)
    _row(
        "VA_VOLCANO_IDENTITY",
        "info",
        "VA SIGMET erupting volcano identity (MT/PSN). Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("va", "volcano", "sigmet", "v1"),
    ),
    _row(
        "VA_ASH_GEOMETRY",
        "info",
        "VA SIGMET ash cloud geometry / forecast position. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("va", "geometry", "sigmet", "v1"),
    ),
    _row(
        "NO_VA_EXP",
        "info",
        "VA SIGMET NO VA EXP absence token. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("va", "no_va_exp", "sigmet", "v1", "c1"),
    ),
    _row(
        "VA_CNL_FIR_MOVED",
        "info",
        "VA SIGMET CNL identifies FIR to which ash has moved. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("va", "cnl", "fir", "sigmet", "v1", "c1"),
    ),
    _row(
        "MISSING_VA_VOLCANO",
        "error",
        "VA SIGMET missing volcano identity (MT … PSN). Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("va", "volcano", "sigmet", "v1"),
    ),
    _row(
        "INVALID_NO_VA_EXP",
        "error",
        "VA SIGMET NO VA EXP must not include VA CLD body. Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("va", "no_va_exp", "sigmet", "v1"),
    ),
    _row(
        "TC_CYCLONE_IDENTITY",
        "info",
        "TC SIGMET includes tropical cyclone identity (TC … PSN). Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("tc", "cyclone", "sigmet", "ev030"),
    ),
    _row(
        "TC_CB_GEOMETRY",
        "info",
        "TC SIGMET CB geometry uses WI … OF TC CENTRE wording. Informational: noted for operator awareness; does not by itself block conversion. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("tc", "geometry", "sigmet", "ev030"),
    ),
    _row(
        "MISSING_TC_IDENTITY",
        "error",
        "TC SIGMET missing cyclone identity (TC … PSN). Error: the TAC does not meet a required format or product rule and should be corrected. Source: EUR Doc 014 public; Annex 3 paywall companion.",
        product="sigmet",
        tags=("tc", "cyclone", "sigmet", "ev030"),
    ),
    _row(
        "MISSING_DTG",
        "error",
        "{product} missing DTG: template field",
        tags=("dtg", "vaa", "tca", "swxa", "vona"),
    ),
    _row(
        "MISSING_VAAC",
        "error",
        "VAA missing VAAC: template field - A2-1",
        product="vaa",
        tags=("vaac", "vaa"),
    ),
    _row(
        "MISSING_VOLCANO",
        "error",
        "VAA missing VOLCANO: template field - F26 theme V1 / A2-1",
        product="vaa",
        tags=("volcano", "vaa", "v1", "f26"),
    ),
    _row(
        "VAA_VOLCANO_UNKNOWN",
        "info",
        "VAA VOLCANO UNKNOWN - exceptional name allowed (F26 theme V1)",
        product="vaa",
        tags=("volcano", "unknown", "vaa", "v1", "f26"),
    ),
    _row(
        "VAA_VOLCANO_UNNAMED",
        "info",
        "VAA VOLCANO UNNAMED - exceptional name allowed (F26 theme V1)",
        product="vaa",
        tags=("volcano", "unnamed", "vaa", "v1", "f26"),
    ),
    _row(
        "VAA_RMK_NIL",
        "info",
        "VAA RMK NIL - remarks inapplicable (F26 theme V1)",
        product="vaa",
        tags=("remarks", "nil", "vaa", "v1", "f26"),
    ),
    _row(
        "VAA_FCST_NO_VA_EXP",
        "info",
        "VAA forecast NO VA EXP - status NO_VOLCANIC_ASH_EXPECTED (F26 theme V1)",
        product="vaa",
        tags=("forecast", "no_va_exp", "vaa", "v1", "f26"),
    ),
    _row(
        "VAA_NO_FURTHER_ADVISORIES",
        "info",
        "VAA NXT ADVISORY NO FURTHER ADVISORIES - next time inapplicable (F26 theme V1)",
        product="vaa",
        tags=("next_advisory", "vaa", "v1", "f26"),
    ),
    _row(
        "MISSING_MAX_WIND",
        "error",
        "TCA missing MAX WIND: template field - A2-2",
        product="tca",
        tags=("max_wind", "tca"),
    ),
    _row(
        "MISSING_TC",
        "error",
        "TCA missing TC: template field - F27 theme T1 / A2-2",
        product="tca",
        tags=("tropical_cyclone", "tca", "t1", "f27"),
    ),
    _row(
        "TCA_CYCLONE_UNNAMED",
        "info",
        "TCA TC UNNAMED - exceptional name allowed (F27 theme T1)",
        product="tca",
        tags=("tropical_cyclone", "unnamed", "tca", "t1", "f27"),
    ),
    _row(
        "TCA_RMK_NIL",
        "info",
        "TCA RMK NIL - remarks inapplicable (F27 theme T1)",
        product="tca",
        tags=("remarks", "nil", "tca", "t1", "f27"),
    ),
    _row(
        "TCA_NO_MSG_EXP",
        "info",
        "TCA NXT MSG NO MSG EXP - next time inapplicable (F27 theme T1)",
        product="tca",
        tags=("next_advisory", "tca", "t1", "f27"),
    ),
    _row(
        "TCA_CB_NIL",
        "info",
        "TCA CB NIL - CB missing (F27 theme T1)",
        product="tca",
        tags=("cb", "nil", "tca", "t1", "f27"),
    ),
    _row(
        "MISSING_SWXC",
        "error",
        "SWXA missing SWXC: template field - F28 theme SX1 / A2-3",
        product="swxa",
        tags=("swxc", "swxa", "sx1", "f28"),
    ),
    _row(
        "SWXA_RMK_NIL",
        "info",
        "SWXA RMK NIL - remarks inapplicable (F28 theme SX1)",
        product="swxa",
        tags=("remarks", "nil", "swxa", "sx1", "f28"),
    ),
    _row(
        "SWXA_FCST_NO_SWX_EXP",
        "info",
        "SWXA forecast NO SWX EXP - no space weather expected (F28 theme SX1)",
        product="swxa",
        tags=("forecast", "no_swx_exp", "swxa", "sx1", "f28"),
    ),
    _row(
        "SWXA_NO_FURTHER_ADVISORIES",
        "info",
        "SWXA NXT ADVISORY NO FURTHER ADVISORIES - next time inapplicable (F28 theme SX1)",
        product="swxa",
        tags=("next_advisory", "swxa", "sx1", "f28"),
    ),
    _row(
        "MISSING_SVO",
        "error",
        "VONA missing SVO: template field - F32 theme V1 / A7-1",
        product="vona",
        tags=("svo", "vona", "v1", "f32"),
    ),
    _row(
        "MISSING_VONA_VOLCANO",
        "error",
        "VONA missing VOLCANO: template field - F32 theme V1 / A7-1",
        product="vona",
        tags=("volcano", "vona", "v1", "f32"),
    ),
    _row(
        "VONA_ONSET_NIL",
        "info",
        "VONA ONSET NIL - onsetTime omitted (F32 theme V1)",
        product="vona",
        tags=("onset", "nil", "vona", "v1", "f32"),
    ),
    _row(
        "VONA_DUR_NIL",
        "info",
        "VONA DUR NIL - duration omitted (F32 theme V1)",
        product="vona",
        tags=("duration", "nil", "vona", "v1", "f32"),
    ),
)

_BY_CODE: dict[str, IssueSpec] = {spec.code: spec for spec in ISSUES}


def catalog_entries(*, product: str | None = None) -> tuple[IssueSpec, ...]:
    """
    Return registry rows for HTTP/docs catalog export.

    Parameters
    ----------
    product :
        Optional product filter (case-insensitive). When set, include rows whose
        ``product`` field matches or whose ``tags`` contain that product id
        (e.g. ``metar``, ``speci``). When omitted, return the full registry.

    Returns
    -------
    tuple[IssueSpec, ...]
        Frozen catalog rows in registry order.
    """
    if product is None or not str(product).strip():
        return ISSUES
    key = str(product).strip().lower()
    selected: list[IssueSpec] = []
    for spec in ISSUES:
        if spec.product is not None and spec.product.lower() == key:
            selected.append(spec)
            continue
        if key in {tag.lower() for tag in spec.tags}:
            selected.append(spec)
    return tuple(selected)


def by_code(code: str) -> IssueSpec:
    """
    Return the registered ``IssueSpec`` for ``code``.

    Parameters
    ----------
    code :
        Public issue code.

    Returns
    -------
    IssueSpec
        Registry row.

    Raises
    ------
    KeyError
        If ``code`` is not registered.
    """
    try:
        return _BY_CODE[code]
    except KeyError:
        raise KeyError(f"unknown lint issue code: {code!r}") from None


def issue_from(
    code: str,
    *,
    message: str | None = None,
    location: str | None = None,
    start: int | None = None,
    end: int | None = None,
    **kwargs: object,
) -> Issue:
    """
    Build an ``Issue`` from a registry row.

    Parameters
    ----------
    code :
        Registered public code.
    message :
        Optional full message override (skips template formatting).
    location :
        Optional token / field hint.
    start, end :
        Optional character offsets into the TAC string.
    **kwargs :
        Passed to ``message_template.format`` when ``message`` is omitted.

    Returns
    -------
    Issue
        Structured finding using the registry default severity.

    Raises
    ------
    KeyError
        If ``code`` is not registered.
    """
    spec = by_code(code)
    if message is not None:
        text = message
    elif kwargs:
        text = spec.message_template.format(**kwargs)
    else:
        text = spec.message_template
    return Issue(
        severity=spec.severity,
        code=spec.code,
        message=text,
        location=location,
        start=start,
        end=end,
    )


__all__ = ["ISSUES", "IssueSpec", "by_code", "catalog_entries", "issue_from"]
