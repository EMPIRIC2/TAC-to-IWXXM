"""XSD validation against vendored IWXXM schemas (F2 extract; D-S008-T21-sch)."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.models import Issue
from iwxxm_validate.paths import xsd_path

# lxml ships without complete type stubs; bind as Any for strict basedpyright.
etree: Any = _lxml_etree

logger = logging.getLogger(__name__)


@lru_cache(maxsize=16)
def _compile_schema(iwxxm_version: str) -> Any | None:
    """
    Compile and cache the XSD for ``iwxxm_version``.

    Returns ``None`` when the schema has known non-blocking import gaps
    (parity with backend F2 for 2025-x substitutionGroup issues).
    """
    path = xsd_path(iwxxm_version)
    try:
        doc = etree.parse(str(path))
        return etree.XMLSchema(doc)
    except etree.XMLSchemaParseError as exc:
        msg = str(exc)
        if "substitutionGroup" in msg and "2025" in iwxxm_version:
            logger.warning("Non-blocking XSD import gap for %s: %s", iwxxm_version, msg)
            return None
        raise


def validate_xsd(xml_content: str, iwxxm_version: str) -> list[Issue]:
    """
    Validate IWXXM XML against the vendored XSD.

    Parameters
    ----------
    xml_content :
        XML document text.
    iwxxm_version :
        IWXXM release line.

    Returns
    -------
    list of Issue
        Empty on success; otherwise schema / parse findings.
    """
    try:
        xml_doc = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        return [
            Issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML parsing failed: {exc}",
                layer="xsd",
                location=f"line {getattr(exc, 'lineno', '?')}",
            )
        ]

    try:
        schema = _compile_schema(iwxxm_version)
    except FileNotFoundError as exc:
        return [
            Issue(
                severity="error",
                code="SCHEMA_NOT_AVAILABLE",
                message=str(exc),
                layer="xsd",
            )
        ]
    except etree.XMLSchemaParseError as exc:
        return [
            Issue(
                severity="error",
                code="SCHEMA_PARSE_ERROR",
                message=f"Failed to parse XSD schema: {exc}",
                layer="xsd",
            )
        ]
    except Exception as exc:  # noqa: BLE001 — surface as structured issue
        return [
            Issue(
                severity="error",
                code="SCHEMA_NOT_AVAILABLE",
                message=f"Schema version {iwxxm_version} not available: {exc}",
                layer="xsd",
            )
        ]

    if schema is None:
        return [
            Issue(
                severity="warning",
                code="SCHEMA_IMPORT_WARNING",
                message=(
                    f"Schema has import resolution issues for {iwxxm_version} (non-blocking); strict XSD check skipped"
                ),
                layer="xsd",
            )
        ]

    try:
        ok = bool(schema.validate(xml_doc))
    except Exception as exc:  # noqa: BLE001
        return [
            Issue(
                severity="error",
                code="XSD_VALIDATE_ERROR",
                message=f"XSD validation error: {exc}",
                layer="xsd",
            )
        ]

    if ok:
        return []

    issues: list[Issue] = []
    for err in schema.error_log:
        issues.append(
            Issue(
                severity="error",
                code="XSD_VALIDATION_ERROR",
                message=str(err.message),
                layer="xsd",
                location=f"line {err.line}, column {err.column}",
            )
        )
    if not issues:
        issues.append(
            Issue(
                severity="error",
                code="XSD_VALIDATION_ERROR",
                message="XSD validation failed with no error log details",
                layer="xsd",
            )
        )
    return issues


def clear_xsd_cache() -> None:
    """Clear compiled XSD cache (tests)."""
    _compile_schema.cache_clear()


__all__ = ["clear_xsd_cache", "validate_xsd"]
