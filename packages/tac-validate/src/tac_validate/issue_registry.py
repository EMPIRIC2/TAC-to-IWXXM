"""Maintainable TAC lint issue registry (F15 / ADR-028).

Rules import ``IssueSpec`` rows via ``by_code`` / ``issue_from`` instead of inventing
severity or code string literals. Catalog export (``make catalog-regen``) iterates
``ISSUES``.
"""

from __future__ import annotations

import string

import msgspec

from tac_validate.models import Issue

# Catalog / soft-preview may render templates without live kwargs. Prefer a
# readable noun over literal ``{product}`` braces in operator copy.
_OPERATOR_FORMAT_DEFAULTS: dict[str, str] = {
    "product": "report",
    "token": "token",
    "expected": "supported products",
    "keywords": "product keywords",
    "hit": "phenomena",
    "family": "register",
}


def format_operator_message(template: str, **kwargs: object) -> str:
    """
    Format a registry message template for operators.

    Missing placeholders use safe defaults (for example ``product`` → ``report``)
    so catalog and soft-preview never show raw ``{product}`` braces.

    Parameters
    ----------
    template : str
        Registry ``message_template``.
    **kwargs : object
        Values for placeholders (``product``, ``token``, …).

    Returns
    -------
    str
        Formatted operator text with no unresolved ``{…}`` field names when
        defaults cover the template.
    """
    merged: dict[str, object] = {**_OPERATOR_FORMAT_DEFAULTS, **kwargs}
    for _literal, field_name, _format_spec, _conversion in string.Formatter().parse(template):
        if field_name and field_name not in merged:
            # Omit unknown fields rather than echo the field name or braces.
            merged[field_name] = ""
    try:
        return template.format(**merged)
    except (KeyError, ValueError, IndexError):
        return _strip_unresolved_braces(template, merged)


def _strip_unresolved_braces(template: str, values: dict[str, object]) -> str:
    """Best-effort substitute then remove leftover ``{name}`` / ``{name!r}``."""
    text = template
    for key, value in values.items():
        text = text.replace(f"{{{key}!r}}", repr(value))
        text = text.replace(f"{{{key}}}", str(value))
    parts: list[str] = []
    for literal, field_name, format_spec, conversion in string.Formatter().parse(text):
        parts.append(literal or "")
        if field_name is None:
            continue
        if field_name in values:
            value = values[field_name]
            if conversion == "r":
                parts.append(repr(value))
            elif conversion == "s":
                parts.append(str(value))
            elif conversion == "a":
                parts.append(ascii(value))
            elif format_spec:
                parts.append(format(value, format_spec))
            else:
                parts.append(str(value))
        else:
            # Omit unknown fields rather than show braces.
            continue
    return "".join(parts)


class IssueSpec(msgspec.Struct, frozen=True):
    """
    One registered lint issue definition.

    Parameters
    ----------
    code : str
        Stable SCREAMING_SNAKE public id.
    severity : str
        Default ``error``, ``warning``, or ``info``.
    message_template : str
        Human message; may include ``str.format`` placeholders (e.g. ``{product}``).
    product : str or None
        Optional product tag for catalog filtering (``None`` = shared / multi-product).
    tags : tuple[str, ...]
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
    """
    Internal helper ``_row``.

    Parameters
    ----------
    code : object
        Argument ``code``.
    severity : object
        Argument ``severity``.
    message_template : object
        Argument ``message_template``.
    product : object
        Argument ``product``.
    tags : object
        Argument ``tags``.

    Returns
    -------
    object
        Return value.
    """
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
        "Product {product!r} is not supported. Use one of: {expected}.",
        tags=("parse_gate",),
    ),
    _row(
        "EMPTY_TAC",
        "error",
        "The TAC text is empty. Paste or load a report before conversion.",
        tags=("parse_gate", "body"),
    ),
    _row(
        "MISSING_PRODUCT_KEYWORD",
        "error",
        "This {product} must include one of these keywords: {keywords}.",
        tags=("parse_gate", "header"),
    ),
    _row(
        "INVALID_AHL",
        "error",
        "The WMO abbreviated heading is not valid. Correct the heading before conversion.",
        tags=("bulletin", "ahl", "parse_gate"),
    ),
    _row(
        "MISSING_TERMINATOR",
        "info",
        "Bulletin reports should end with '='. Add the terminator before you publish.",
        tags=("terminator", "metar", "speci", "taf"),
    ),
    _row(
        "MISSING_CCCC",
        "error",
        "This {product} is missing the ICAO station location (CCCC). Add the four-letter location.",
        tags=("station", "metar", "speci", "taf", "sigmet", "airmet"),
    ),
    _row(
        "MISSING_OBS_TIME",
        "error",
        "This {product} is missing the observation time (ddhhmmZ). Add the time group.",
        tags=("time", "metar", "speci"),
    ),
    _row(
        "MISSING_DECODE_MATCH",
        "error",
        "This {product} could not be decoded for theme checks. Fix the TAC so decode succeeds.",
        tags=("match", "metar"),
    ),
    _row(
        "PARTIAL_DECODE",
        "warning",
        "Some TAC tokens were not decoded. Conversion can still continue; review residual groups.",
        tags=("decode", "residual"),
    ),
    _row(
        "ODD_FIELD_ORDER",
        "warning",
        "This {product} has groups out of the usual order (CCCC, then ddhhmmZ, then wind). Review the group order.",
        tags=("order", "station", "time", "metar", "speci"),
    ),
    _row(
        "MISSING_WIND",
        "error",
        "This {product} is missing the surface wind group. Add the wind group.",
        tags=("wind", "metar", "speci"),
    ),
    _row(
        "MISSING_VISIBILITY",
        "error",
        "This {product} is missing visibility or CAVOK. Add a visibility group or CAVOK.",
        tags=("visibility", "metar", "speci"),
    ),
    _row(
        "INVALID_VISIBILITY",
        "error",
        "This {product} has an invalid visibility token. Use statute miles (SM), meters, or CAVOK.",
        tags=("visibility", "metar", "speci"),
    ),
    _row(
        "INVALID_WEATHER",
        "error",
        "This {product} has an invalid present-weather token {token!r}. Correct the weather group.",
        tags=("weather", "metar", "speci"),
    ),
    _row(
        "MISSING_TEMP_DEWPOINT",
        "error",
        "This {product} is missing temperature/dewpoint (tt/td). Add the temperature group.",
        tags=("temperature", "metar", "speci"),
    ),
    _row(
        "DEWPOINT_NOT_OBSERVABLE",
        "info",
        "This {product} shows dewpoint as not observable (tt///). Temperature is present. Conversion can continue.",
        tags=("temperature", "metar", "speci", "auto"),
    ),
    _row(
        "MISSING_QNH",
        "error",
        "This {product} is missing QNH or altimeter (Qnnnn or Annnn). Add the pressure group.",
        tags=("pressure", "metar", "speci"),
    ),
    _row(
        "INVALID_CLOUD_TOKEN",
        "error",
        "This {product} has an invalid cloud or VV token {token!r}. Correct the cloud group.",
        tags=("cloud", "metar", "speci"),
    ),
    _row(
        "CLOUD_CB_OR_TCU",
        "info",
        "This {product} cloud group includes convective type CB or TCU. Conversion can continue.",
        tags=("cloud", "metar", "speci", "cb", "tcu"),
    ),
    _row(
        "CLOUD_TYPE_NOT_OBSERVABLE",
        "info",
        "This {product} cloud group uses /// because convective cloud type was not observed. Conversion can continue.",
        tags=("cloud", "metar", "speci", "auto"),
    ),
    _row(
        "REMARK_US_EXTENSION",
        "info",
        "This {product} includes US remark groups used with the US IWXXM profile. Conversion can continue.",
        tags=("remark", "metar", "speci", "iwxxm_us"),
    ),
    _row(
        "INVALID_REMARK",
        "error",
        "This {product} has a malformed remark group {token!r}. Correct the remark.",
        tags=("remark", "metar", "speci", "iwxxm_us"),
    ),
    _row(
        "MALFORMED_SOURCE_TOKEN",
        "warning",
        "This {product} has a token that looks garbled or mistyped: {token!r}. Review and correct it.",
        tags=("parse_gate", "metar", "speci", "taf", "sigmet"),
    ),
    _row(
        "AUTO_PRESENT",
        "info",
        "This {product} was produced by an automatic station (AUTO). Conversion can continue.",
        tags=("modifier", "metar", "speci"),
    ),
    _row(
        "CA_STATUTE_MILE_VIS",
        "info",
        "This {product} uses statute-mile visibility (Canadian MANOBS). Conversion can continue.",
        tags=("visibility", "metar", "speci", "ca_eccc", "manobs"),
    ),
    _row(
        "CA_ALTIMETER_INHG",
        "info",
        "This {product} uses an inch-of-mercury altimeter (A####) (Canadian MANOBS). Conversion can continue.",
        tags=("pressure", "metar", "speci", "ca_eccc", "manobs"),
    ),
    _row(
        "CA_REMARK_MANOBS",
        "info",
        "This {product} includes Canadian REMARKS (MANOBS). Conversion can continue.",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs"),
    ),
    _row(
        "CA_REMARK_PRESRR",
        "info",
        "This {product} includes PRESRR (pressure rising rapidly). Conversion can continue.",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs", "presrr"),
    ),
    _row(
        "CA_REMARK_PRESFR",
        "info",
        "This {product} includes PRESFR (pressure falling rapidly). Conversion can continue.",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs", "presfr"),
    ),
    _row(
        "CA_REMARK_NOSPECI",
        "info",
        "This {product} includes NOSPECI (no specials). Conversion can continue.",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs", "nospeci"),
    ),
    _row(
        "CA_REMARK_SECTOR_VIS",
        "info",
        "This {product} includes a sector visibility remark. Conversion can continue.",
        tags=("remark", "metar", "speci", "ca_eccc", "manobs", "visibility"),
    ),
    _row(
        "CA_ALTIMETER_NOT_OBS",
        "info",
        "This {product} shows altimeter as not observable (A////). Conversion can continue.",
        tags=("pressure", "metar", "speci", "ca_eccc", "manobs"),
    ),
    _row(
        "CA_METAR_LWIS",
        "info",
        "This {product} is a Limited Weather Information System (LWIS) report. Conversion can continue.",
        tags=("metar", "ca_eccc", "manobs", "lwis"),
    ),
    _row(
        "CA_METAR_SAWR",
        "info",
        "This {product} is a Surface Aviation Weather Report (SAWR). Conversion can continue.",
        tags=("metar", "ca_eccc", "manobs", "sawr"),
    ),
    _row(
        "CA_TAF_NCLWS",
        "info",
        "This {product} includes non-convective low-level wind shear (WS). Conversion can continue.",
        tags=("taf", "ca_eccc", "manair", "nclws"),
    ),
    _row(
        "IN_TAF_TX_TN_OMITTED",
        "info",
        "This {product} omits TX/TN temperature extremes. India Meteorological Department TAFs often do this. Conversion can continue.",
        product="TAF",
        tags=("taf", "in_imd", "temperature", "tx_tn"),
    ),
    _row(
        "US_TAF_BECMG_FORBIDDEN",
        "error",
        "This {product} must not use BECMG under the US FAA/NWS profile. Remove BECMG or change the profile.",
        product="TAF",
        tags=("taf", "iwxxm_us", "us_faa_nws"),
    ),
    _row(
        "US_TAF_TEMPO_MAX_4H",
        "error",
        "This {product} TEMPO period is longer than the 4-hour US FAA/NWS maximum. Shorten TEMPO.",
        product="TAF",
        tags=("taf", "iwxxm_us", "us_faa_nws"),
    ),
    _row(
        "US_TAF_PROB40_NOT_USED",
        "error",
        "This {product} must not use PROB40 under the US FAA/NWS profile. Remove PROB40 or change the profile.",
        product="TAF",
        tags=("taf", "iwxxm_us", "us_faa_nws", "prob40"),
    ),
    _row(
        "US_METAR_STATUTE_MILE_VIS",
        "info",
        "This {product} uses statute-mile visibility with SM (US METAR). Conversion can continue.",
        tags=("metar", "speci", "iwxxm_us", "us_faa_nws", "visibility"),
    ),
    _row(
        "US_METAR_INHG_ALTIMETER",
        "info",
        "This {product} uses an inch-of-mercury altimeter (A####) (US METAR). Conversion can continue.",
        tags=("metar", "speci", "iwxxm_us", "us_faa_nws", "pressure"),
    ),
    _row(
        "CA_METAR_UP_AWOS_ONLY",
        "info",
        "This {product} uses UP (unknown precipitation), which is AWOS-only under the Canadian profile. Conversion can continue.",
        tags=("metar", "speci", "ca_eccc", "manobs", "awos", "up"),
    ),
    _row(
        "US_SWXA_SATCOM_NOT_ISSUED",
        "error",
        "This {product} must not issue SATCOM space weather under the US FAA/NWS profile. Remove SATCOM or change the profile.",
        product="SWXA",
        tags=("swxa", "iwxxm_us", "us_faa_nws", "satcom"),
    ),
    _row(
        "US_TCA_OBSERVED_CB_NOT_PROVIDED",
        "error",
        "This {product} must set observed CB to NIL under the US FAA/NWS profile. Observed CB is not provided.",
        product="TCA",
        tags=("tca", "iwxxm_us", "us_faa_nws", "cb"),
    ),
    _row(
        "CA_AIRMET_GFA",
        "info",
        "This {product} encodes a MANAIR GFA compound phenomenon. Conversion can continue.",
        tags=("airmet", "ca_eccc", "manair", "gfa"),
    ),
    _row(
        "COR_PRESENT",
        "info",
        "This {product} is a correction (COR). Conversion can continue.",
        tags=("modifier", "metar", "speci", "taf"),
    ),
    _row(
        "AMD_PRESENT",
        "info",
        "This {product} is an amendment (AMD). Conversion can continue.",
        product="taf",
        tags=("modifier", "taf"),
    ),
    _row(
        "NIL_REPORT",
        "info",
        "This {product} is a NIL report (no observation or forecast for the period). Conversion can continue.",
        tags=("nil", "metar", "speci", "taf"),
    ),
    _row(
        "CNL_REPORT",
        "info",
        "This {product} is a cancel (CNL) that withdraws a prior forecast. Conversion can continue.",
        product="taf",
        tags=("cnl", "taf"),
    ),
    _row(
        "INVALID_NIL",
        "error",
        "This {product} is marked NIL but still has body groups. NIL must stand alone. Remove the body content.",
        tags=("nil", "metar", "speci", "taf"),
    ),
    _row(
        "MULTI_REPORT_BULLETIN",
        "info",
        "This {product} bulletin has more than one TAC report. Convert one report at a time.",
        tags=("bulletin", "metar", "speci", "taf", "sigmet", "airmet", "one_report"),
    ),
    _row(
        "NOSIG_PRESENT",
        "info",
        "This {product} includes NOSIG (no significant change expected). Conversion can continue.",
        tags=("trend", "metar", "speci"),
    ),
    _row(
        "TEMPO_PRESENT",
        "info",
        "This {product} includes TEMPO (temporary fluctuations). Conversion can continue.",
        tags=("trend", "change", "metar", "speci", "taf"),
    ),
    _row(
        "RVR_PRESENT",
        "info",
        "This {product} includes runway visual range (RVR) groups. Conversion can continue.",
        tags=("rvr", "metar", "speci"),
    ),
    _row(
        "INVALID_RVR",
        "error",
        "This {product} has an invalid RVR token {token!r}. Correct the RVR group.",
        tags=("rvr", "metar", "speci"),
    ),
    _row(
        "WIND_VRB_OR_GUST",
        "info",
        "This {product} wind group uses variable direction (VRB) and/or a gust. Conversion can continue.",
        tags=("wind", "metar", "speci"),
    ),
    _row(
        "INVALID_WIND",
        "error",
        "This {product} has an invalid wind token {token!r}. Correct the wind group.",
        tags=("wind", "metar", "speci"),
    ),
    _row(
        "MISSING_ISSUE_TIME",
        "error",
        "This TAF is missing the issue time (ddhhmmZ). Add the issue time.",
        product="taf",
        tags=("time", "taf"),
    ),
    _row(
        "MISSING_VALIDITY",
        "error",
        "This TAF is missing the validity period (ddhh/ddhh). Add the validity period.",
        product="taf",
        tags=("validity", "taf"),
    ),
    _row(
        "INVALID_CNL_SHAPE",
        "error",
        "This TAF CNL must end the message. Remove content after CNL.",
        product="taf",
        tags=("cnl", "taf"),
    ),
    _row(
        "FM_PRESENT",
        "info",
        "This {product} includes an FM (from) change group. Conversion can continue.",
        product="taf",
        tags=("change", "taf", "fm"),
    ),
    _row(
        "BECMG_PRESENT",
        "info",
        "This {product} includes a BECMG (becoming) change group. Conversion can continue.",
        product="taf",
        tags=("change", "taf", "becmg"),
    ),
    _row(
        "PROB_PRESENT",
        "info",
        "This {product} includes a PROB30 or PROB40 probability group. Conversion can continue.",
        product="taf",
        tags=("change", "taf", "prob"),
    ),
    _row(
        "TL_PRESENT",
        "info",
        "This {product} includes a TL (until) time qualifier. Conversion can continue.",
        product="taf",
        tags=("change", "taf", "tl"),
    ),
    _row(
        "AT_PRESENT",
        "info",
        "This {product} includes an AT time qualifier. Conversion can continue.",
        product="taf",
        tags=("change", "taf", "at"),
    ),
    _row(
        "INVALID_PROB",
        "error",
        "This {product} has an invalid PROB group. Use only PROB30 or PROB40, and do not qualify BECMG or FM with PROB.",
        product="taf",
        tags=("change", "taf", "prob"),
    ),
    _row(
        "PROB_PERIOD_WITHOUT_TEMPO",
        "warning",
        "This {product} has a standalone PROB30/40 period. Annex 3 allows that form; engines emit PROB_PRESENT for awareness. True defects stay INVALID_PROB.",
        product="taf",
        tags=("change", "taf", "prob"),
    ),
    _row(
        "TX_TN_PRESENT",
        "info",
        "This {product} includes TX/TN temperature forecasts on the base forecast. Conversion can continue.",
        product="taf",
        tags=("temperature", "taf"),
    ),
    _row(
        "INVALID_TX_TN",
        "error",
        "This {product} places TX/TN outside the base forecast. Move TX/TN to the base forecast only.",
        product="taf",
        tags=("temperature", "taf"),
    ),
    _row(
        "CAVOK_PRESENT",
        "info",
        "This {product} includes CAVOK (ceiling and visibility OK). Conversion can continue.",
        tags=("cavok", "metar", "speci", "taf"),
    ),
    _row(
        "NSC_PRESENT",
        "info",
        "This {product} includes NSC (no significant cloud). Conversion can continue.",
        tags=("cloud", "metar", "speci", "taf"),
    ),
    _row(
        "NSC_WITH_CLOUD_LAYERS",
        "warning",
        "This {product} combines NSC with FEW/SCT/BKN/OVC in the same group. Review before you publish.",
        tags=("cloud", "metar", "speci", "taf"),
    ),
    _row(
        "NCD_PRESENT",
        "info",
        "This {product} includes NCD (no cloud detected), often from AUTO stations. Conversion can continue.",
        tags=("cloud", "metar", "speci", "auto"),
    ),
    _row(
        "NSW_PRESENT",
        "info",
        "This {product} includes NSW (nil significant weather). Conversion can continue.",
        tags=("weather", "metar", "speci", "taf"),
    ),
    _row(
        "VV_OMIT",
        "info",
        "This {product} uses VV///. For this product, omit vertical visibility when there is no nil reason. Conversion can continue.",
        product="taf",
        tags=("cloud", "taf", "vv"),
    ),
    _row(
        "VV_NOT_OBSERVABLE",
        "info",
        "This {product} uses VV/// (vertical visibility not observable). Conversion can continue.",
        tags=("cloud", "metar", "speci", "vv"),
    ),
    _row(
        "WX_NOT_OBSERVABLE",
        "info",
        "This {product} present weather uses // (phenomena not observable). Conversion can continue.",
        tags=("weather", "metar", "speci"),
    ),
    _row(
        "WIND_DIR_VARIATION",
        "info",
        "This {product} includes wind direction variation (dddVddd). Conversion can continue.",
        tags=("wind", "metar", "speci"),
    ),
    _row(
        "MISSING_VALID",
        "error",
        "This {product} is missing the VALID period (ddhhmm/ddhhmm). Add the validity period.",
        tags=("valid", "sigmet", "airmet"),
    ),
    _row(
        "MULTIPLE_PHENOMENA",
        "error",
        "This {product} encodes more than one phenomenon family ({hit}). Keep one phenomenon family per report.",
        tags=("phenomenon", "sigmet", "airmet"),
    ),
    # S059 / EV-050 / #959 - offline WMO register membership (Validated)
    _row(
        "UNKNOWN_WMO_MEMBERSHIP",
        "error",
        "This {product} token {token!r} is not in the WMO register ({family}). Correct the token.",
        tags=("membership", "wmo", "weather", "cloud", "phenomenon"),
    ),
    # F23 theme G1 - general SIGMET exceptional (#733 / research G1)
    _row(
        "SIGMET_CNL",
        "info",
        "This SIGMET is a cancel (CNL). Conversion can continue.",
        product="sigmet",
        tags=("cnl", "sigmet"),
    ),
    _row(
        "STNR_MOVEMENT",
        "info",
        "This SIGMET/AIRMET is stationary (STNR). Conversion can continue.",
        product="sigmet",
        tags=("stnr", "movement", "sigmet", "airmet"),
    ),
    _row(
        "POINT_LOCATION",
        "info",
        "This SIGMET uses a single-point location. Conversion can continue.",
        product="sigmet",
        tags=("geometry", "point", "sigmet"),
    ),
    _row(
        "SINGLE_ALTITUDE",
        "info",
        "This SIGMET uses one altitude for lower and upper. Conversion can continue.",
        product="sigmet",
        tags=("altitude", "sigmet"),
    ),
    _row(
        "POLYGON_LOCATION",
        "info",
        "This SIGMET uses WI polygon or line geometry. Conversion can continue.",
        product="sigmet",
        tags=("geometry", "polygon", "sigmet"),
    ),
    _row(
        "TOP_ABV_OR_BLW",
        "info",
        "This SIGMET/AIRMET uses TOP ABV or TOP BLW level wording. Conversion can continue.",
        product="sigmet",
        tags=("altitude", "top", "sigmet", "airmet"),
    ),
    _row(
        "INVALID_SIGMET_CNL",
        "error",
        "This SIGMET CNL must omit phenomenon and analysis body. Remove the body content.",
        product="sigmet",
        tags=("cnl", "sigmet"),
    ),
    _row(
        "INVALID_SIGMET_COR",
        "error",
        "This SIGMET must not use COR. Cancel and re-issue instead.",
        product="sigmet",
        tags=("cor", "sigmet"),
    ),
    _row(
        "INVALID_STNR_MOVEMENT",
        "error",
        "This SIGMET/AIRMET has STNR together with MOV. Remove one of the conflicting movement groups.",
        product="sigmet",
        tags=("stnr", "movement", "sigmet", "airmet"),
    ),
    _row(
        "DVLPG_AREA_QUALIFIER",
        "error",
        "This convective SIGMET has a misplaced or incomplete DVLPG (developing) qualifier. Put DVLPG AREA after the FROM ring.",
        product="sigmet",
        tags=("geometry", "convective", "sigmet", "us_nws"),
    ),
    # F23 theme G2 - sequence / validity / FIR / OBS·FCST / intensity (#733)
    _row(
        "SIGMET_SEQUENCE",
        "info",
        "This {product} includes a SEQUENCE number. Conversion can continue.",
        product="sigmet",
        tags=("sequence", "sigmet"),
    ),
    _row(
        "FIR_OR_CTA",
        "info",
        "This SIGMET names FIR, CTA, or UIR airspace. Conversion can continue.",
        product="sigmet",
        tags=("fir", "cta", "sigmet"),
    ),
    _row(
        "OBS_OR_FCST",
        "info",
        "This SIGMET/AIRMET includes OBS or FCST. Conversion can continue.",
        product="sigmet",
        tags=("obs", "fcst", "sigmet", "airmet"),
    ),
    _row(
        "INTENSITY_CHANGE",
        "info",
        "This SIGMET/AIRMET includes intensity change (INTSF, WKN, or NC). Conversion can continue.",
        product="sigmet",
        tags=("intensity", "sigmet", "airmet"),
    ),
    _row(
        "MISSING_SEQUENCE",
        "error",
        "This SIGMET/AIRMET is missing a sequence number. Add the sequence number.",
        product="sigmet",
        tags=("sequence", "sigmet", "airmet"),
    ),
    _row(
        "INVALID_VALIDITY_DURATION",
        "error",
        "This SIGMET VALID period is longer than 4 hours (WS). Shorten the validity period.",
        product="sigmet",
        tags=("valid", "sigmet"),
    ),
    _row(
        "MISSING_FIR_OR_CTA",
        "error",
        "This SIGMET/AIRMET is missing FIR, CTA, or UIR airspace identity. Add the airspace name.",
        product="sigmet",
        tags=("fir", "cta", "sigmet", "airmet"),
    ),
    _row(
        "MISSING_OBS_OR_FCST",
        "error",
        "This SIGMET/AIRMET is missing OBS or FCST. Add OBS or FCST.",
        product="sigmet",
        tags=("obs", "fcst", "sigmet", "airmet"),
    ),
    # F23 theme V1 - VA SIGMET (#739 / research V1)
    _row(
        "VA_VOLCANO_IDENTITY",
        "info",
        "This VA SIGMET names the erupting volcano (name or MT PSN). Conversion can continue.",
        product="sigmet",
        tags=("va", "volcano", "sigmet"),
    ),
    _row(
        "VA_ASH_GEOMETRY",
        "info",
        "This VA SIGMET includes ash cloud geometry or forecast position. Conversion can continue.",
        product="sigmet",
        tags=("va", "geometry", "sigmet"),
    ),
    _row(
        "NO_VA_EXP",
        "info",
        "This VA SIGMET includes NO VA EXP (no volcanic ash expected). Conversion can continue.",
        product="sigmet",
        tags=("va", "no_va_exp", "sigmet"),
    ),
    _row(
        "VA_CNL_FIR_MOVED",
        "info",
        "This VA SIGMET CNL names the FIR to which ash has moved. Conversion can continue.",
        product="sigmet",
        tags=("va", "cnl", "fir", "sigmet"),
    ),
    _row(
        "MISSING_VA_VOLCANO",
        "error",
        "This VA SIGMET is missing volcano identity (name or MT … PSN). Add the volcano identity.",
        product="sigmet",
        tags=("va", "volcano", "sigmet"),
    ),
    _row(
        "INVALID_NO_VA_EXP",
        "error",
        "This VA SIGMET with NO VA EXP must not include a VA CLD body. Remove the ash-cloud body.",
        product="sigmet",
        tags=("va", "no_va_exp", "sigmet"),
    ),
    _row(
        "TC_CYCLONE_IDENTITY",
        "info",
        "This TC SIGMET includes tropical cyclone identity (TC … PSN). Conversion can continue.",
        product="sigmet",
        tags=("tc", "cyclone", "sigmet"),
    ),
    _row(
        "TC_CB_GEOMETRY",
        "info",
        "This TC SIGMET CB geometry uses WI … OF TC CENTRE wording. Conversion can continue.",
        product="sigmet",
        tags=("tc", "geometry", "sigmet"),
    ),
    _row(
        "MISSING_TC_IDENTITY",
        "error",
        "This TC SIGMET is missing cyclone identity (TC … PSN). Add the cyclone identity.",
        product="sigmet",
        tags=("tc", "cyclone", "sigmet"),
    ),
    _row(
        "MISSING_DTG",
        "error",
        "This {product} is missing the DTG field. Add DTG.",
        tags=("dtg", "vaa", "tca", "swxa", "vona"),
    ),
    _row(
        "MISSING_VAAC",
        "error",
        "This VAA is missing the VAAC field. Add VAAC.",
        product="vaa",
        tags=("vaac", "vaa"),
    ),
    _row(
        "MISSING_VOLCANO",
        "error",
        "This VAA is missing the VOLCANO field. Add VOLCANO.",
        product="vaa",
        tags=("volcano", "vaa"),
    ),
    _row(
        "VAA_VOLCANO_UNKNOWN",
        "info",
        "This VAA uses VOLCANO UNKNOWN. That exceptional name is allowed. Conversion can continue.",
        product="vaa",
        tags=("volcano", "unknown", "vaa"),
    ),
    _row(
        "VAA_VOLCANO_UNNAMED",
        "info",
        "This VAA uses VOLCANO UNNAMED. That exceptional name is allowed. Conversion can continue.",
        product="vaa",
        tags=("volcano", "unnamed", "vaa"),
    ),
    _row(
        "VAA_RMK_NIL",
        "info",
        "This VAA has RMK NIL (remarks not applicable). Conversion can continue.",
        product="vaa",
        tags=("remarks", "nil", "vaa"),
    ),
    _row(
        "VAA_FCST_NO_VA_EXP",
        "info",
        "This VAA forecast is NO VA EXP (no volcanic ash expected). Conversion can continue.",
        product="vaa",
        tags=("forecast", "no_va_exp", "vaa"),
    ),
    _row(
        "VAA_NO_FURTHER_ADVISORIES",
        "info",
        "This VAA next advisory is NO FURTHER ADVISORIES. Conversion can continue.",
        product="vaa",
        tags=("next_advisory", "vaa"),
    ),
    _row(
        "MISSING_MAX_WIND",
        "error",
        "This TCA is missing the MAX WIND field. Add MAX WIND.",
        product="tca",
        tags=("max_wind", "tca"),
    ),
    _row(
        "MISSING_TC",
        "error",
        "This TCA is missing the TC field. Add TC.",
        product="tca",
        tags=("tropical_cyclone", "tca"),
    ),
    _row(
        "TCA_CYCLONE_UNNAMED",
        "info",
        "This TCA uses TC UNNAMED. That exceptional name is allowed. Conversion can continue.",
        product="tca",
        tags=("tropical_cyclone", "unnamed", "tca"),
    ),
    _row(
        "TCA_RMK_NIL",
        "info",
        "This TCA has RMK NIL (remarks not applicable). Conversion can continue.",
        product="tca",
        tags=("remarks", "nil", "tca"),
    ),
    _row(
        "TCA_NO_MSG_EXP",
        "info",
        "This TCA next message is NO MSG EXP. Conversion can continue.",
        product="tca",
        tags=("next_advisory", "tca"),
    ),
    _row(
        "TCA_CB_NIL",
        "info",
        "This TCA has CB NIL (no CB). Conversion can continue.",
        product="tca",
        tags=("cb", "nil", "tca"),
    ),
    _row(
        "MISSING_SWXC",
        "error",
        "This SWXA is missing the SWXC field. Add SWXC.",
        product="swxa",
        tags=("swxc", "swxa"),
    ),
    _row(
        "SWXA_RMK_NIL",
        "info",
        "This SWXA has RMK NIL (remarks not applicable). Conversion can continue.",
        product="swxa",
        tags=("remarks", "nil", "swxa"),
    ),
    _row(
        "SWXA_FCST_NO_SWX_EXP",
        "info",
        "This SWXA forecast is NO SWX EXP (no space weather expected). Conversion can continue.",
        product="swxa",
        tags=("forecast", "no_swx_exp", "swxa"),
    ),
    _row(
        "SWXA_NO_FURTHER_ADVISORIES",
        "info",
        "This SWXA next advisory is NO FURTHER ADVISORIES. Conversion can continue.",
        product="swxa",
        tags=("next_advisory", "swxa"),
    ),
    _row(
        "MISSING_SVO",
        "error",
        "This VONA is missing the SVO field. Add SVO.",
        product="vona",
        tags=("svo", "vona"),
    ),
    _row(
        "MISSING_VONA_VOLCANO",
        "error",
        "This VONA is missing the VOLCANO field. Add VOLCANO.",
        product="vona",
        tags=("volcano", "vona"),
    ),
    _row(
        "VONA_ONSET_NIL",
        "info",
        "This VONA has ONSET NIL (onset time omitted). Conversion can continue.",
        product="vona",
        tags=("onset", "nil", "vona"),
    ),
    _row(
        "VONA_DUR_NIL",
        "info",
        "This VONA has DUR NIL (duration omitted). Conversion can continue.",
        product="vona",
        tags=("duration", "nil", "vona"),
    ),
)

_BY_CODE: dict[str, IssueSpec] = {spec.code: spec for spec in ISSUES}


def catalog_entries(*, product: str | None = None) -> tuple[IssueSpec, ...]:
    """
    Return registry rows for HTTP/docs catalog export.

    Parameters
    ----------
    product : str or None, optional
        Optional product filter (case-insensitive). When set, include rows whose
        ``product`` field matches or whose ``tags`` contain that product id
        (e.g. ``metar``, ``speci``). When omitted, return the full registry. By default ``None``.

    Returns
    -------
    tuple[IssueSpec, ...]
        Frozen catalog rows in registry order.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (catalog_entries)
    2
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
    code : str
        Public issue code.

    Returns
    -------
    IssueSpec
        Registry row.

    Raises
    ------
    KeyError
        If ``code`` is not registered.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (by_code)
    2
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
    code : str
        Registered public code.
    message : str or None, optional
        Optional full message override (skips template formatting). By default ``None``.
    location : str or None, optional
        Optional token / field hint.
        start, end :
        Optional character offsets into the TAC string. By default ``None``.
    **kwargs : object
        Passed to ``message_template.format`` when ``message`` is omitted.
    start : int or None, optional
        Start. By default ``None``.
    end : int or None, optional
        End. By default ``None``.

    Returns
    -------
    Issue
        Structured finding using the registry default severity.

    Raises
    ------
    KeyError
        If ``code`` is not registered.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (issue_from)
    2
    """
    spec = by_code(code)
    text = message if message is not None else format_operator_message(spec.message_template, **kwargs)
    return Issue(
        severity=spec.severity,
        code=spec.code,
        message=text,
        location=location,
        start=start,
        end=end,
    )


__all__ = [
    "ISSUES",
    "IssueSpec",
    "by_code",
    "catalog_entries",
    "format_operator_message",
    "issue_from",
]
