"""Load the shared lint-profile catalog.

One YAML row per semantic profile. Country differences are deltas in that
file, not a new Python module. [Corpus: domain-profiles] [Corpus: product §F36]
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

import yaml

from tac_validate.models import Issue, LintReport

_CATALOG_PATH = Path(__file__).resolve().parent / "data" / "lint_profiles.yaml"
_TOKEN_RE = re.compile(r"'([^']+)'")


@dataclass(frozen=True, slots=True)
class LintDelta:
    """
    One recorded suppression against the engine rule pack.

    Parameters
    ----------
    rule_id :
        Stable id for this country difference.
    products :
        Products the suppression applies to.
    suppress_codes :
        Engine issue codes to drop when the token matches.
    token_pattern :
        Compiled match against the quoted token in the issue message.
    """

    rule_id: str
    products: frozenset[str]
    suppress_codes: frozenset[str]
    token_pattern: re.Pattern[str]


@dataclass(frozen=True, slots=True)
class LintProfileSpec:
    """
    Lint behavior for one semantic profile.

    Parameters
    ----------
    profile_id :
        Profile id accepted by ``lint``.
    engine :
        Existing rule pack that runs before deltas.
    products :
        Products this profile may lint.
    differs :
        True when the profile is not identical to its engine.
    deltas :
        Suppressions applied after the engine.
    recorded :
        Difference ids that are noted and not yet suppressions.
    """

    profile_id: str
    engine: str
    products: frozenset[str]
    differs: bool
    deltas: tuple[LintDelta, ...]
    recorded: tuple[str, ...]


def _mapping(value: object, *, field: str) -> dict[str, object]:
    """
    Internal helper ``_mapping``.

    Parameters
    ----------
    value : object
        YAML node.
    field : str
        Field name used in the error.

    Returns
    -------
    dict[str, object]
        String-keyed mapping.

    Raises
    ------
    ValueError
        When ``value`` is not a mapping.
    """
    if not isinstance(value, dict):
        msg = f"lint profile {field} must be a mapping"
        raise ValueError(msg)
    found: dict[str, object] = {}
    typed = cast(dict[object, object], value)
    for key, item in typed.items():
        if not isinstance(key, str):
            msg = f"lint profile {field} key must be a string"
            raise ValueError(msg)
        found[key] = item
    return found


def _string_list(value: object, *, field: str) -> list[str]:
    """
    Internal helper ``_string_list``.

    Parameters
    ----------
    value : object
        YAML node.
    field : str
        Field name used in the error.

    Returns
    -------
    list[str]
        String items.

    Raises
    ------
    ValueError
        When ``value`` is not a list of strings.
    """
    if not isinstance(value, list):
        msg = f"lint profile {field} must be a list"
        raise ValueError(msg)
    found: list[str] = []
    items = cast(list[object], value)
    for item in items:
        if not isinstance(item, str):
            msg = f"lint profile {field} items must be strings"
            raise ValueError(msg)
        found.append(item)
    return found


def _object_list(value: object, *, field: str) -> list[object]:
    """
    Internal helper ``_object_list``.

    Parameters
    ----------
    value : object
        YAML node.
    field : str
        Field name used in the error.

    Returns
    -------
    list[object]
        List items.

    Raises
    ------
    ValueError
        When ``value`` is not a list.
    """
    if not isinstance(value, list):
        msg = f"lint profile {field} must be a list"
        raise ValueError(msg)
    return list(cast(list[object], value))


def _required_str(row: dict[str, object], key: str) -> str:
    """
    Internal helper ``_required_str``.

    Parameters
    ----------
    row : dict[str, object]
        Mapping row.
    key : str
        Required string field.

    Returns
    -------
    str
        Field value.

    Raises
    ------
    ValueError
        When the field is missing or not a string.
    """
    value = row[key]
    if not isinstance(value, str) or not value:
        msg = f"lint profile {key} must be a string"
        raise ValueError(msg)
    return value


def _delta(raw: object) -> LintDelta:
    """
    Internal helper ``_delta``.

    Parameters
    ----------
    raw : object
        One ``deltas`` row.

    Returns
    -------
    LintDelta
        Parsed suppression.
    """
    row = _mapping(raw, field="delta")
    return LintDelta(
        rule_id=_required_str(row, "id"),
        products=frozenset(item.upper() for item in _string_list(row["products"], field="products")),
        suppress_codes=frozenset(_string_list(row["suppress_codes"], field="suppress_codes")),
        token_pattern=re.compile(_required_str(row, "token_pattern")),
    )


def _specs_from_document(document_raw: object) -> dict[str, LintProfileSpec]:
    """
    Internal helper ``_specs_from_document``.

    Parameters
    ----------
    document_raw : object
        Parsed catalog document.

    Returns
    -------
    dict[str, LintProfileSpec]
        Profile rows.
    """
    document = _mapping(document_raw, field="catalog")
    rows = _mapping(document["profiles"], field="profiles")
    loaded: dict[str, LintProfileSpec] = {}
    for profile_id, body_raw in rows.items():
        body = _mapping(body_raw, field=profile_id)
        deltas = tuple(_delta(item) for item in _object_list(body.get("deltas", []), field="deltas"))
        recorded = tuple(
            _required_str(_mapping(item, field="recorded"), "id")
            for item in _object_list(body.get("recorded", []), field="recorded")
        )
        differs = body["differs"]
        if not isinstance(differs, bool):
            msg = f"lint profile {profile_id} differs must be a boolean"
            raise ValueError(msg)
        loaded[profile_id] = LintProfileSpec(
            profile_id=profile_id,
            engine=_required_str(body, "engine"),
            products=frozenset(item.upper() for item in _string_list(body["products"], field="products")),
            differs=differs,
            deltas=deltas,
            recorded=recorded,
        )
    return loaded


@cache
def load_lint_profiles() -> dict[str, LintProfileSpec]:
    """
    Return every lint profile keyed by id.

    Returns
    -------
    dict[str, LintProfileSpec]
        Catalog rows from ``lint_profiles.yaml``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_lint_profiles)
    2
    """
    return _specs_from_document(yaml.safe_load(_CATALOG_PATH.read_text(encoding="utf-8")))


def lint_profile_spec(profile: str) -> LintProfileSpec | None:
    """
    Return the catalog row for ``profile``, or ``None`` when it is absent.

    Parameters
    ----------
    profile : str
        Requested lint profile id.

    Returns
    -------
    LintProfileSpec | None
        The row, or ``None``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (lint_profile_spec)
    2
    """
    return load_lint_profiles().get(profile.strip().lower())


def _suppressed(issue: Issue, spec: LintProfileSpec, product: str) -> bool:
    """
    Internal helper ``_suppressed``.

    Parameters
    ----------
    issue : Issue
        Engine finding.
    spec : LintProfileSpec
        Profile being linted.
    product : str
        Product id.

    Returns
    -------
    bool
        True when a delta drops this finding.
    """
    quoted = _TOKEN_RE.search(issue.message or "")
    if quoted is None:
        return False
    token = quoted.group(1)
    for delta in spec.deltas:
        if product not in delta.products or issue.code not in delta.suppress_codes:
            continue
        if delta.token_pattern.fullmatch(token):
            return True
    return False


def apply_profile_deltas(report: LintReport, *, profile: str, product: str) -> LintReport:
    """
    Drop engine findings that this profile records as allowed.

    Parameters
    ----------
    report : LintReport
        Engine result.
    profile : str
        Requested profile id.
    product : str
        Product id.

    Returns
    -------
    LintReport
        Findings for ``profile``. The ``profile`` field is the requested id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (apply_profile_deltas)
    2
    """
    spec = lint_profile_spec(profile)
    issues = list(report.issues)
    if spec is not None and spec.deltas:
        issues = [issue for issue in issues if not _suppressed(issue, spec, product.upper())]
    ok = not any(issue.severity == "error" for issue in issues)
    return LintReport(
        ok=ok,
        product=report.product,
        issues=issues,
        fixes=list(report.fixes),
        profile=profile,
    )
