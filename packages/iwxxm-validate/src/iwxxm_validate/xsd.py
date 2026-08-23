"""XSD validation against vendored IWXXM schemas (F2 extract; D-S008-T21-sch)."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.models import Issue
from iwxxm_validate.paths import xsd_path

_XSD_LAYER_DEFAULT = "xsd"

# lxml ships without complete type stubs; bind as Any for strict basedpyright.
etree: Any = _lxml_etree

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def _compile_schema_file(xsd_file: str) -> Any | None:
    """
    Compile and cache an arbitrary XSD path (product extension schemas).
    """
    path = Path(xsd_file)
    try:
        doc = etree.parse(str(path))
        return etree.XMLSchema(doc)
    except etree.XMLSchemaParseError as exc:
        msg = str(exc)
        if "substitutionGroup" in msg:
            logger.warning("Non-blocking XSD import gap for %s: %s", path, msg)
            return None
        raise


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


def _validate_against_schema(
    xml_content: str,
    schema: Any | None,
    *,
    layer: str,
    schema_label: str,
) -> list[Issue]:
    try:
        xml_doc = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        return [
            Issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML parsing failed: {exc}",
                layer=layer,
                location=f"line {getattr(exc, 'lineno', '?')}",
            )
        ]

    if schema is None:
        return [
            Issue(
                severity="warning",
                code="SCHEMA_IMPORT_WARNING",
                message=(
                    f"Schema has import resolution issues for {schema_label} (non-blocking); strict XSD check skipped"
                ),
                layer=layer,
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
                layer=layer,
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
                layer=layer,
                location=f"line {err.line}, column {err.column}",
            )
        )
    if not issues:
        issues.append(
            Issue(
                severity="error",
                code="XSD_VALIDATION_ERROR",
                message="XSD validation failed with no error log details",
                layer=layer,
            )
        )
    return issues


def validate_xsd_at_path(
    xml_content: str,
    xsd_file: Path | str,
    *,
    layer: str = _XSD_LAYER_DEFAULT,
) -> list[Issue]:
    """
    Validate XML against an explicit XSD file path.

    Parameters
    ----------
    xml_content :
        XML document text.
    xsd_file :
        Absolute or relative path to the XSD schema file.
    layer :
        Issue ``layer`` / stage id for findings (e.g. ``ca_xsd``).

    Returns
    -------
    list of Issue
        Empty on success; otherwise schema / parse findings.
    """
    path = Path(xsd_file)
    if not path.is_file():
        return [
            Issue(
                severity="error",
                code="SCHEMA_NOT_AVAILABLE",
                message=f"XSD not found at {path}",
                layer=layer,
            )
        ]
    try:
        schema = _compile_schema_file(str(path.resolve()))
    except etree.XMLSchemaParseError as exc:
        return [
            Issue(
                severity="error",
                code="SCHEMA_PARSE_ERROR",
                message=f"Failed to parse XSD schema: {exc}",
                layer=layer,
            )
        ]
    except Exception as exc:  # noqa: BLE001
        return [
            Issue(
                severity="error",
                code="SCHEMA_NOT_AVAILABLE",
                message=f"Schema at {path} not available: {exc}",
                layer=layer,
            )
        ]
    return _validate_against_schema(xml_content, schema, layer=layer, schema_label=str(path))


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
        schema = _compile_schema(iwxxm_version)
    except FileNotFoundError as exc:
        return [
            Issue(
                severity="error",
                code="SCHEMA_NOT_AVAILABLE",
                message=str(exc),
                layer=_XSD_LAYER_DEFAULT,
            )
        ]
    except etree.XMLSchemaParseError as exc:
        return [
            Issue(
                severity="error",
                code="SCHEMA_PARSE_ERROR",
                message=f"Failed to parse XSD schema: {exc}",
                layer=_XSD_LAYER_DEFAULT,
            )
        ]
    except Exception as exc:  # noqa: BLE001 — surface as structured issue
        return [
            Issue(
                severity="error",
                code="SCHEMA_NOT_AVAILABLE",
                message=f"Schema version {iwxxm_version} not available: {exc}",
                layer=_XSD_LAYER_DEFAULT,
            )
        ]

    return _validate_against_schema(
        xml_content,
        schema,
        layer=_XSD_LAYER_DEFAULT,
        schema_label=iwxxm_version,
    )


def clear_xsd_cache() -> None:
    """Clear compiled XSD cache (tests)."""
    _compile_schema.cache_clear()
    _compile_schema_file.cache_clear()


__all__ = ["clear_xsd_cache", "validate_xsd", "validate_xsd_at_path"]
