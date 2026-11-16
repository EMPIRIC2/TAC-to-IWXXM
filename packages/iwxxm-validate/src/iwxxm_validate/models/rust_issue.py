"""Native Rust engine issue wire shape and conversion helpers.

Examples
--------
>>> 1 + 1  # docstring smoke
2

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, TypedDict

from iwxxm_validate.models.report import Issue


class RustIssueDict(TypedDict, total=False):
    """
    One finding dict returned by ``_rust.validate_document``.

    Wire keys match the PyO3 ``ValidationIssue`` fields exported as dicts.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    """

    severity: str
    code: str
    message: str
    layer: str
    location: str | None


def issue_from_rust_mapping(
    item: Mapping[str, Any] | RustIssueDict,
    *,
    default_layer: str = "xsd",
    layer_override: str | None = None,
) -> Issue:
    """
    Convert one Rust issue mapping into an :class:`Issue`.

    Parameters
    ----------
    item : Mapping[str, Any] or RustIssueDict
        Raw finding from the native engine.
    default_layer : str, optional
        Layer when ``item`` omits ``layer``. By default ``'xsd'``.
    layer_override : str or None, optional
        When set, force ``Issue.layer`` to this value.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    Returns
    -------
    Issue
        Package report finding with stable wire field names.
    """
    layer = layer_override if layer_override is not None else str(item.get("layer", default_layer))
    location = item.get("location")
    return Issue(
        severity=str(item.get("severity", "error")),
        code=str(item.get("code", "NATIVE_ISSUE")),
        message=str(item.get("message", "")),
        layer=layer,
        location=str(location) if location is not None else None,
    )


def issues_from_rust(
    raw: Sequence[Mapping[str, Any] | RustIssueDict],
    *,
    default_layer: str = "xsd",
    layer_map: Mapping[str, str] | None = None,
    stage_id: str | None = None,
) -> list[Issue]:
    """
    Convert a sequence of Rust issue mappings into :class:`Issue` rows.

    Parameters
    ----------
    raw : Sequence[Mapping[str, Any] or RustIssueDict]
        Native engine findings.
    default_layer : str, optional
        Fallback layer. By default ``'xsd'``.
    layer_map : Mapping[str, str] or None, optional
        Optional map from Rust ``layer`` to stage ids (CA layered path).
    stage_id : str or None, optional
        When set with ``layer_map``, prefer ``stage_id`` unless the mapped
        stage equals ``stage_id``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    Returns
    -------
    list[Issue]
        Converted findings.
    """
    issues: list[Issue] = []
    for item in raw:
        rust_layer = str(item.get("layer", default_layer))
        if layer_map is not None and stage_id is not None:
            mapped = layer_map.get(rust_layer, stage_id)
            override = mapped if mapped == stage_id else stage_id
            issues.append(issue_from_rust_mapping(item, default_layer=default_layer, layer_override=override))
        else:
            issues.append(issue_from_rust_mapping(item, default_layer=default_layer))
    return issues


__all__ = ["RustIssueDict", "issue_from_rust_mapping", "issues_from_rust"]
