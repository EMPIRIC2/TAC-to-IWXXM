"""Public ``convert()`` entrypoint (F6 seven products annex3 + iwxxm_us METAR/SPECI)."""

from __future__ import annotations

import re
from typing import Any, Callable, cast
from xml.sax.saxutils import escape

from tac2iwxxm.models import ConvertIssue, ConvertResult
from tac2iwxxm.products.metar_speci import parse_metar_speci
from tac2iwxxm.products.sigmet_airmet import parse_airmet, parse_sigmet
from tac2iwxxm.products.taf import parse_taf
from tac2iwxxm.products.vaa_tca import parse_tca, parse_vaa
from tac2iwxxm.profiles.annex3 import emit_metar_speci_annex3
from tac2iwxxm.profiles.annex3_products import (
    emit_airmet_annex3,
    emit_sigmet_annex3,
    emit_taf_annex3,
    emit_tca_annex3,
    emit_vaa_annex3,
)
from tac2iwxxm.profiles.iwxxm_us import (
    emit_airmet_iwxxm_us,
    emit_metar_speci_iwxxm_us,
    emit_sigmet_iwxxm_us,
    emit_taf_iwxxm_us,
)

_SUPPORTED_PRODUCTS = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA"})
_SUPPORTED_PROFILES = frozenset({"annex3", "iwxxm_us"})
_US_PRODUCTS = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET"})
_REPORT_STATUSES = frozenset({"NORMAL", "AMENDMENT", "CORRECTION"})

# Map MALFORMED_REMARKS message needles → token regexes for editor spans (S011 T2.2).
_REMARK_SPAN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("malformed AO", re.compile(r"\bAO(?![12]\b)\w*\b")),
    ("malformed SLP", re.compile(r"\bSLP(?!\d{3}\b)\w*\b")),
    ("malformed PK WND", re.compile(r"\bPK\s+WND\b")),
)
_RMK_TOKEN = re.compile(r"\bRMK\b")


_PREVIEW_ROOTS = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA"})
_PREVIEW_NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
}

# Official *-translation-failed examples mark unreliable TAC with INVALID (FAQ §8.6).
_UNRELIABLE_TAC = re.compile(r"\bINVALID\b", re.IGNORECASE)
_PRODUCT_LEAD = {
    "METAR": re.compile(r"^\s*METAR\b", re.IGNORECASE),
    "SPECI": re.compile(r"^\s*SPECI\b", re.IGNORECASE),
    "TAF": re.compile(r"^\s*TAF\b", re.IGNORECASE),
    "SIGMET": re.compile(r"^\s*(?:[A-Z]{4}\s+)?SIGMET\b", re.IGNORECASE | re.MULTILINE),
    "AIRMET": re.compile(r"^\s*(?:[A-Z]{4}\s+)?AIRMET\b", re.IGNORECASE | re.MULTILINE),
    "VAA": re.compile(r"VA\s+ADVISORY\b", re.IGNORECASE),
    "TCA": re.compile(r"TC\s+ADVISORY\b", re.IGNORECASE),
}
_QUARANTINE_ROOT = {
    "METAR": "METAR",
    "SPECI": "SPECI",
    "TAF": "TAF",
    "SIGMET": "SIGMET",
    "AIRMET": "AIRMET",
    "VAA": "VolcanicAshAdvisory",
    "TCA": "TropicalCycloneAdvisory",
}
_STATION_AFTER_PRODUCT = re.compile(
    r"^\s*(?:METAR|SPECI|TAF)\s+(?:COR\s+)?(?P<station>[A-Z][A-Z0-9]{3})\b",
    re.IGNORECASE,
)


def _content_bounds(tac: str) -> tuple[int, int]:
    """Return inclusive start / exclusive end of stripped TAC content in ``tac``."""
    stripped = tac.strip()
    if not stripped:
        return 0, len(tac)
    leading = len(tac) - len(tac.lstrip())
    return leading, leading + len(stripped)


def _preview_stub_xml(product: str, iwxxm_version: str, reason: str) -> str:
    """
    Emit a minimal best-effort IWXXM shell for soft-preview (not for publication).

    Parameters
    ----------
    product :
        Product root element name (e.g. ``METAR``).
    iwxxm_version :
        Release line used to pick the IWXXM namespace.
    reason :
        Short human-readable failure note embedded as an XML comment.

    Returns
    -------
    str
        IWXXM-looking XML document with a nil observation.
    """
    from xml.sax.saxutils import escape

    root = product.upper() if product.upper() in _PREVIEW_ROOTS else "METAR"
    ns = _PREVIEW_NS.get(iwxxm_version, _PREVIEW_NS["2025-2"])
    gml_id = f"{root.lower()}.preview.failed"
    note = escape(reason[:240])
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<iwxxm:{root} xmlns:iwxxm="{ns}" xmlns:gml="http://www.opengis.net/gml/3.2" '
        f'gml:id="{gml_id}" reportStatus="NORMAL">\n'
        f"  <!-- soft-preview: {note} -->\n"
        '  <iwxxm:observation nilReason="http://codes.wmo.int/common/nil/missing"/>\n'
        f"</iwxxm:{root}>\n"
    )


def _tac_looks_like_product(tac: str, product: str) -> bool:
    """Return True when TAC appears to be the requested product (header / keyword)."""
    pattern = _PRODUCT_LEAD.get(product)
    if pattern is None:
        return False
    return pattern.search(tac) is not None


def _should_quarantine(tac: str, product: str) -> bool:
    """
    Whether failed/unreliable TAC should emit ``translationFailedTAC`` quarantine.

    Explicit ``INVALID`` (official failed examples) or a product-shaped TAC that
    cannot be translated operationally.
    """
    if _UNRELIABLE_TAC.search(tac):
        return True
    return _tac_looks_like_product(tac, product)


def _quarantine_xml(product: str, tac: str, iwxxm_version: str) -> str:
    """
    Emit official-shaped quarantine shell with ``@translationFailedTAC``.

    Parameters
    ----------
    product :
        F6 product code.
    tac :
        Original TAC text (stored on translationFailedTAC).
    iwxxm_version :
        IWXXM release line for namespace.

    Returns
    -------
    str
        Quarantine IWXXM document (no operational observation/baseForecast).
    """
    from datetime import datetime, timezone
    from xml.sax.saxutils import escape

    root = _QUARANTINE_ROOT.get(product, product)
    ns = _PREVIEW_NS.get(iwxxm_version, _PREVIEW_NS["2025-2"])
    gml_id = f"{product.lower()}.translation.failed"
    failed_tac = escape(" ".join(tac.split()))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    station_m = _STATION_AFTER_PRODUCT.search(tac)
    station = station_m.group("station").upper() if station_m else "YUDO"
    aerodrome = ""
    if product in {"METAR", "SPECI", "TAF"}:
        aerodrome = f"""  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.{station.lower()}">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.{station.lower()}">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{station}</aixm:designator>
          <aixm:locationIndicatorICAO>{station}</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
"""
    time_block = f"""  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{now}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
"""
    if product in {"METAR", "SPECI"}:
        time_block += f"""  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>{now}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
"""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<iwxxm:{root} xmlns:iwxxm="{ns}" '
        'xmlns:gml="http://www.opengis.net/gml/3.2" '
        'xmlns:aixm="http://www.aixm.aero/schema/5.1.1" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'gml:id="{gml_id}" '
        'reportStatus="NORMAL" '
        'permissibleUsage="OPERATIONAL" '
        'translatedBulletinID="TTAAiiCCCYYGGgg" '
        f'translatedBulletinReceptionTime="{now}" '
        'translationCentreDesignator="YUZZ" '
        'translationCentreName="Fictional translation centre" '
        f'translationTime="{now}" '
        f'translationFailedTAC="{failed_tac}">\n'
        f"{time_block}{aerodrome}"
        f"</iwxxm:{root}>\n"
    )


def _remark_span(tac: str, message: str) -> tuple[int | None, int | None]:
    """Best-effort character span for a US REMARKS diagnostic message."""
    for needle, pattern in _REMARK_SPAN_PATTERNS:
        if needle in message:
            match = pattern.search(tac)
            if match is not None:
                return match.start(), match.end()
    return None, None


class ConvertError(ValueError):
    """
    Fatal conversion failure.

    Parameters
    ----------
    message :
        Human-readable description.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


def _parse(product: str, tac: str) -> dict[str, Any]:
    parsers: dict[str, Callable[..., dict[str, Any]]] = {
        "METAR": parse_metar_speci,
        "SPECI": parse_metar_speci,
        "TAF": parse_taf,
        "SIGMET": parse_sigmet,
        "AIRMET": parse_airmet,
        "VAA": parse_vaa,
        "TCA": parse_tca,
    }
    return parsers[product](tac, product=product)


def _emit(product: str, profile: str, ir: dict[str, Any], iwxxm_version: str) -> str:
    if product in {"METAR", "SPECI"}:
        if profile == "iwxxm_us":
            return emit_metar_speci_iwxxm_us(ir, product=product, iwxxm_version=iwxxm_version)
        return emit_metar_speci_annex3(ir, product=product, iwxxm_version=iwxxm_version)
    if product == "TAF":
        if profile == "iwxxm_us":
            return emit_taf_iwxxm_us(ir, iwxxm_version=iwxxm_version)
        return emit_taf_annex3(ir, iwxxm_version=iwxxm_version)
    if product == "SIGMET":
        if profile == "iwxxm_us":
            return emit_sigmet_iwxxm_us(ir, iwxxm_version=iwxxm_version)
        return emit_sigmet_annex3(ir, iwxxm_version=iwxxm_version)
    if product == "AIRMET":
        if profile == "iwxxm_us":
            return emit_airmet_iwxxm_us(ir, iwxxm_version=iwxxm_version)
        return emit_airmet_annex3(ir, iwxxm_version=iwxxm_version)
    if product == "VAA":
        return emit_vaa_annex3(ir, iwxxm_version=iwxxm_version)
    if product == "TCA":
        return emit_tca_annex3(ir, iwxxm_version=iwxxm_version)
    raise ValueError(f"no emitter for product {product!r}")


_ROOT_OPEN = re.compile(r"(<iwxxm:[A-Za-z]+\b)([^>]*)(>)", re.DOTALL)


def _inject_translation_centre(
    xml: str,
    *,
    designator: str,
    name: str,
) -> str:
    """
    Insert ``translationCentre*`` attributes on the IWXXM root element.

    Parameters
    ----------
    xml : str
        Successful convert document (not a quarantine shell).
    designator : str
        ``translationCentreDesignator`` value.
    name : str
        ``translationCentreName`` value.

    Returns
    -------
    str
        XML with centre attributes on the first ``iwxxm:*`` root start tag.
    """
    extra = f'\n    translationCentreDesignator="{escape(designator)}"\n    translationCentreName="{escape(name)}"'
    match = _ROOT_OPEN.search(xml)
    if match is None:
        return xml
    return xml[: match.start()] + match.group(1) + match.group(2) + extra + match.group(3) + xml[match.end() :]


def convert(
    tac: str,
    *,
    product: str,
    profile: str = "annex3",
    iwxxm_version: str = "2025-2",
    preview: bool = False,
    emit_translation_centre: bool = False,
    translation_centre_designator: str = "",
    translation_centre_name: str = "",
    report_status: str | None = None,
) -> ConvertResult:
    """
    Convert a TAC report to IWXXM XML.

    Parameters
    ----------
    tac :
        TAC text (single report or bulletin containing one report).
    product :
        One of the seven F6 products.
    profile :
        ``annex3`` (default) or ``iwxxm_us`` (METAR/SPECI US extensions; others T5.4–T5.5).
    iwxxm_version :
        Target IWXXM release line.
    preview :
        When ``True``, fatal parse/profile failures still return best-effort stub XML
        (soft-preview / ADR-022). Does not imply Schematron-passed publish.
    emit_translation_centre :
        When ``True``, emit ``translationCentreDesignator`` / ``translationCentreName``
        on successful convert (cross-State / Translation Centre mode; FAQ §14.5).
        Default ``False`` omits them for in-State convert. Quarantine shells always
        include centre attrs (official ``*-translation-failed`` model).
    translation_centre_designator :
        Designator when ``emit_translation_centre`` is true.
    translation_centre_name :
        Human-readable centre name when ``emit_translation_centre`` is true.
    report_status :
        Optional IWXXM ``reportStatus`` override (``NORMAL`` / ``AMENDMENT`` /
        ``CORRECTION``). Used for AHL BBB→reportStatus when the TAC body has no
        COR/AMD keyword (EV-029 M2 / #823 B3). When omitted, emitters keep
        body-derived COR → CORRECTION behavior.

    Returns
    -------
    ConvertResult
        Structured result with XML, IR, and issues.
    """
    product_u = product.upper()
    profile_l = profile.lower()

    def _fail(code: str, message: str, *, span: bool = False) -> ConvertResult:
        span_start = span_end = None
        if span:
            span_start, span_end = _content_bounds(tac)
        issue = ConvertIssue(
            severity="error",
            code=code,
            message=message,
            start=span_start,
            end=span_end,
        )
        xml = _preview_stub_xml(product_u, iwxxm_version, f"{code}: {message}") if preview else None
        return ConvertResult(
            ok=False,
            product=product_u,
            profile=profile_l,
            iwxxm_version=iwxxm_version,
            xml=xml,
            issues=[issue],
        )

    if product_u not in _SUPPORTED_PRODUCTS:
        return _fail("UNSUPPORTED_PRODUCT", f"product {product_u!r} not supported yet")
    if profile_l not in _SUPPORTED_PROFILES:
        return _fail("UNSUPPORTED_PROFILE", f"profile {profile_l!r} not supported yet")
    if profile_l == "iwxxm_us" and product_u not in _US_PRODUCTS:
        return _fail(
            "UNSUPPORTED_PROFILE",
            f"profile iwxxm_us not supported yet for product {product_u!r}",
        )

    status_override: str | None = None
    if report_status is not None:
        status_override = report_status.strip().upper()
        if status_override not in _REPORT_STATUSES:
            return _fail(
                "INVALID_REPORT_STATUS",
                f"report_status {report_status!r} must be one of {sorted(_REPORT_STATUSES)}",
            )

    try:
        if _UNRELIABLE_TAC.search(tac):
            raise ValueError("unreliable TAC marked INVALID — quarantine")
        ir = _parse(product_u, tac)
        if status_override is not None:
            ir = {**ir, "report_status": status_override}
        xml = _emit(product_u, profile_l, ir, iwxxm_version)
    except ValueError as exc:
        message = str(exc)
        if preview:
            return _fail("PARSE_ERROR", message, span=True)
        if _should_quarantine(tac, product_u):
            span_start, span_end = _content_bounds(tac)
            return ConvertResult(
                ok=True,
                product=product_u,
                profile=profile_l,
                iwxxm_version=iwxxm_version,
                xml=_quarantine_xml(product_u, tac.strip(), iwxxm_version),
                issues=[
                    ConvertIssue(
                        severity="warning",
                        code="TRANSLATION_FAILED",
                        message=message,
                        start=span_start,
                        end=span_end,
                    )
                ],
            )
        return _fail("PARSE_ERROR", message, span=True)

    issues: list[ConvertIssue] = []
    if profile_l == "annex3" and product_u in {"METAR", "SPECI"} and ir.get("remarks_present"):
        rmk_match = _RMK_TOKEN.search(tac)
        issues.append(
            ConvertIssue(
                severity="info",
                code="REMARKS_EXCLUDED",
                message=(
                    "REMARKS (RMK) present in TAC but excluded from annex3 IWXXM output; "
                    "use profile=iwxxm_us to retain US remarks"
                ),
                location="remarks",
                start=rmk_match.start() if rmk_match else None,
                end=rmk_match.end() if rmk_match else None,
            )
        )
    if profile_l == "iwxxm_us":
        raw_remarks: object = ir.get("remark_issues")
        if isinstance(raw_remarks, list):
            for item in cast(list[object], raw_remarks):
                message = str(item)
                remark_start, remark_end = _remark_span(tac, message)
                issues.append(
                    ConvertIssue(
                        severity="warning",
                        code="MALFORMED_REMARKS",
                        message=message,
                        location="remarks",
                        start=remark_start,
                        end=remark_end,
                    )
                )

    if emit_translation_centre:
        xml = _inject_translation_centre(
            xml,
            designator=translation_centre_designator,
            name=translation_centre_name,
        )

    return ConvertResult(
        ok=True,
        product=product_u,
        profile=profile_l,
        iwxxm_version=iwxxm_version,
        xml=xml,
        ir=ir,
        issues=issues,
    )


__all__ = ["ConvertError", "convert"]
