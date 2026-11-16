"""Shared CA_ECCC stage helpers (issue remap, Rust stage, well-formed).

Examples
--------
>>> 1 + 1  # docstring smoke
2

"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from iwxxm_validate.ca_eccc_layers import (
    CA_STAGE_LABELS,
    STAGE_WELLFORMED,
    STAGE_WMO_SCH,
    STAGE_WMO_XSD,
)
from iwxxm_validate.ca_eccc_xml import etree
from iwxxm_validate.models import Issue, StageResult, issues_from_rust
from iwxxm_validate.native import rust_module

_RUST_LAYER_TO_STAGE = {
    "wellformed": STAGE_WELLFORMED,
    "xsd": STAGE_WMO_XSD,
    "schematron": STAGE_WMO_SCH,
}


def has_error(issues: Sequence[Issue]) -> bool:
    """
    Return whether any issue has error severity.

    Parameters
    ----------
    issues : Sequence[Issue]
        Findings.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    Returns
    -------
    bool
        ``True`` when an error-severity issue is present.
    """
    return any(issue.severity == "error" for issue in issues)


def remap_issues(issues: Sequence[Issue], stage_id: str) -> list[Issue]:
    """
    Copy issues with ``layer`` set to ``stage_id``.

    Parameters
    ----------
    issues : Sequence[Issue]
        Source findings.
    stage_id : str
        Target stage / layer id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    Returns
    -------
    list[Issue]
        Remapped findings.
    """
    return [
        Issue(
            severity=issue.severity,
            code=issue.code,
            message=issue.message,
            layer=stage_id,
            location=issue.location,
            start=issue.start,
            end=issue.end,
        )
        for issue in issues
    ]


def stage_result(stage_id: str, issues: list[Issue]) -> StageResult:
    """
    Build a :class:`StageResult` for ``stage_id``.

    Parameters
    ----------
    stage_id : str
        Stage id.
    issues : list[Issue]
        Stage findings.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    Returns
    -------
    StageResult
        Stage outcome with operator label.
    """
    return StageResult(
        stage=stage_id,
        label=CA_STAGE_LABELS[stage_id],
        ok=not has_error(issues),
        issues=issues,
    )


def run_rust_stage(
    xml_content: str,
    *,
    xsd_path: str,
    sch_path: str,
    catalog_roots: list[str],
    levels: list[str],
    stage_id: str,
) -> list[Issue]:
    """
    Run the native validator for one CA stage and map findings.

    Parameters
    ----------
    xml_content : str
        IWXXM XML.
    xsd_path : str
        Primary XSD path.
    sch_path : str
        Schematron path.
    catalog_roots : list[str]
        Catalog root directories.
    levels : list[str]
        Native levels to run.
    stage_id : str
        Stage id for issue ``layer``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    Returns
    -------
    list[Issue]
        Mapped findings.
    """
    rust = rust_module()
    assert rust is not None
    raw: list[dict[str, Any]] = rust.validate_document(
        xml_content,
        xsd_path=xsd_path,
        sch_path=sch_path,
        catalog_roots=catalog_roots,
        levels=levels,
    )
    return issues_from_rust(raw, layer_map=_RUST_LAYER_TO_STAGE, stage_id=stage_id)


def run_wellformed_lxml(xml_content: str) -> list[Issue]:
    """
    Check well-formedness via lxml when the Rust engine is unavailable.

    Parameters
    ----------
    xml_content : str
        IWXXM XML.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    Returns
    -------
    list[Issue]
        Empty on success; one ``XML_SYNTAX_ERROR`` on failure.
    """
    try:
        etree.fromstring(xml_content.encode("utf-8"))
        return []
    except etree.XMLSyntaxError as exc:
        return [
            Issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML parsing failed: {exc}",
                layer=STAGE_WELLFORMED,
                location=f"line {getattr(exc, 'lineno', '?')}",
            )
        ]


__all__ = [
    "has_error",
    "remap_issues",
    "run_rust_stage",
    "run_wellformed_lxml",
    "stage_result",
]
