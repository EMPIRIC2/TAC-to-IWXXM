"""Issue registry lookup and Issue construction."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

import string

from tac_validate.issue_registry.rows_a import ISSUES_A
from tac_validate.issue_registry.rows_b import ISSUES_B
from tac_validate.issue_registry.spec import IssueSpec
from tac_validate.models import Issue

ISSUES: tuple[IssueSpec, ...] = ISSUES_A + ISSUES_B
_BY_CODE: dict[str, IssueSpec] = {spec.code: spec for spec in ISSUES}

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

    Examples
    --------
    >>> format_operator_message("This {product} is an amendment (AMD).", product="taf")
    'This TAF is an amendment (AMD).'
    """
    merged: dict[str, object] = dict(_OPERATOR_FORMAT_DEFAULTS)
    for key, raw in kwargs.items():
        if raw is None:
            continue
        text = str(raw).strip()
        if not text:
            continue
        merged[key] = text.upper() if key == "product" else text
    for _literal, field_name, _format_spec, _conversion in string.Formatter().parse(template):
        if field_name and field_name not in merged:
            # Omit unknown fields rather than echo the field name or braces.
            merged[field_name] = ""
    try:
        return template.format(**merged)
    except (KeyError, ValueError, IndexError):
        return _strip_unresolved_braces(template, merged)


def _strip_unresolved_braces(template: str, values: dict[str, object]) -> str:
    """
    Best-effort substitute then remove leftover ``{name}`` / ``{name!r}``.

    Parameters
    ----------
    template : str
        Message template that failed normal ``str.format``.
    values : dict[str, object]
        Placeholder values already merged with operator defaults.

    Returns
    -------
    str
        Operator text with known fields filled and unknown fields omitted.
    """
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
            try:
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
            except (ValueError, TypeError):
                parts.append(str(value))
        else:
            # Omit unknown fields rather than show braces.
            continue
    return "".join(parts)


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
        Passed to ``format_operator_message`` when ``message`` is omitted.
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
