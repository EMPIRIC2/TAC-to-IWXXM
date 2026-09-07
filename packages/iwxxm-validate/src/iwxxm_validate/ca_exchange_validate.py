"""MSC exchange packaging checks for CA_ECCC documents (EV-069 / #1032)."""

from __future__ import annotations

import re
from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.ca_eccc_layers import STAGE_EXCHANGE
from iwxxm_validate.models import Issue

etree: Any = _lxml_etree
_CA_IWXXM_NS = "http://icao.int/iwxxm/3.0"
_CA_EXTENSION_NS = "https://dd.meteo.gc.ca/today/aviation/iwxxm/"
_VALID_REPORT_STATUS = frozenset({"NORMAL", "CORRECTION", "AMENDMENT"})
_VALID_PERMISSIBLE_USAGE = frozenset({"OPERATIONAL", "NON-OPERATIONAL", "TEST"})
_MSC_FILENAME_RE = re.compile(r"^A_[A-Z]{2}[A-Z]{2}\d{2}[A-Z]{4}\d{6}(?:[A-Z0-9]{3})?_C_[A-Z]{4}_\d{14}\.xml$")
_PRODUCT_AHL_TTAAII: dict[str, str] = {
    "METAR": "A_LACN",
    "SPECI": "A_LPCN",
    "TAF": "A_LTCN",
    "AIRMET": "A_LWCN",
    "SIGMET": "A_LSCN",
    "VAA": "A_LUCN",
}
_IWXXM_EXCHANGE_ROOTS = frozenset(
    {"METAR", "SPECI", "TAF", "AIRMET", "SIGMET", "VolcanicAshSIGMET", "TropicalCycloneSIGMET", "VolcanicAshAdvisory"}
)


def validate_ca_exchange_packaging(
    xml_content: str,
    *,
    product: str | None = None,
    ahl_header: str | None = None,
    expected_filename: str | None = None,
    require_translation_centre: bool = False,
) -> list[Issue]:
    """
    Validate MSC datamart exchange metadata on a CA IWXXM document.

    Parameters
    ----------
    xml_content :
        IWXXM XML document.
    product :
        API product enum used to cross-check an optional AHL header.
    ahl_header :
        Optional WMO AHL header (``A_LACN31…``) supplied by the caller.
    expected_filename :
        Optional MSC filename to validate against the datamart pattern.
    require_translation_centre :
        When ``True``, require ``translationCentre*`` attrs on the document root.

    Returns
    -------
    list[Issue]
        Advisory-free errors for missing operational attributes or header mismatch.
    """
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        return [
            Issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML parsing failed: {exc}",
                layer=STAGE_EXCHANGE,
            )
        ]

    issues: list[Issue] = []
    qname = etree.QName(root)
    local_name = qname.localname
    namespace = qname.namespace
    is_ca_substitution = namespace == _CA_EXTENSION_NS and local_name in {"LWIS", "SAWR"}
    is_wmo_product = namespace == _CA_IWXXM_NS and local_name in _IWXXM_EXCHANGE_ROOTS
    if not is_ca_substitution and not is_wmo_product:
        issues.append(
            Issue(
                severity="error",
                code="CA_EXCHANGE_NAMESPACE",
                message="Canadian operational documents must use IWXXM 3.0 or national substitution roots",
                layer=STAGE_EXCHANGE,
            )
        )

    report_status = root.get("reportStatus")
    if not report_status:
        issues.append(
            Issue(
                severity="error",
                code="CA_EXCHANGE_REPORT_STATUS",
                message="Missing reportStatus attribute on document root",
                layer=STAGE_EXCHANGE,
            )
        )
    elif report_status not in _VALID_REPORT_STATUS:
        issues.append(
            Issue(
                severity="error",
                code="CA_EXCHANGE_REPORT_STATUS",
                message=f"Unsupported reportStatus value: {report_status!r}",
                layer=STAGE_EXCHANGE,
            )
        )

    permissible_usage = root.get("permissibleUsage")
    if not permissible_usage:
        issues.append(
            Issue(
                severity="error",
                code="CA_EXCHANGE_PERMISSIBLE_USAGE",
                message="Missing permissibleUsage attribute on document root",
                layer=STAGE_EXCHANGE,
            )
        )
    elif permissible_usage not in _VALID_PERMISSIBLE_USAGE:
        issues.append(
            Issue(
                severity="error",
                code="CA_EXCHANGE_PERMISSIBLE_USAGE",
                message=f"Unsupported permissibleUsage value: {permissible_usage!r}",
                layer=STAGE_EXCHANGE,
            )
        )

    if root.get("{http://www.opengis.net/gml/3.2}id") is None:
        issues.append(
            Issue(
                severity="error",
                code="CA_EXCHANGE_GML_ID",
                message="Document root must include a gml:id",
                layer=STAGE_EXCHANGE,
            )
        )

    if ahl_header and product:
        expected = _PRODUCT_AHL_TTAAII.get(product.upper())
        if expected and not ahl_header.startswith(expected):
            issues.append(
                Issue(
                    severity="error",
                    code="CA_EXCHANGE_AHL_PRODUCT",
                    message=f"AHL header {ahl_header!r} does not match product {product!r} (expected {expected})",
                    layer=STAGE_EXCHANGE,
                )
            )

    if expected_filename is not None and not _MSC_FILENAME_RE.match(expected_filename.strip()):
        issues.append(
            Issue(
                severity="error",
                code="CA_EXCHANGE_FILENAME",
                message=f"Filename {expected_filename!r} does not match MSC exchange pattern",
                layer=STAGE_EXCHANGE,
            )
        )

    if require_translation_centre:
        designator = root.get("translationCentreDesignator")
        centre_name = root.get("translationCentreName")
        if not designator or not centre_name:
            issues.append(
                Issue(
                    severity="error",
                    code="CA_EXCHANGE_TRANSLATION_CENTRE",
                    message="Missing translationCentreDesignator or translationCentreName on document root",
                    layer=STAGE_EXCHANGE,
                )
            )

    return issues


__all__ = ["validate_ca_exchange_packaging"]
