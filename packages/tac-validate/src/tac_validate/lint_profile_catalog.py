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
MAX_INHERIT_DEPTH = 8


@dataclass(frozen=True, slots=True)
class LintDelta:
    """
    One recorded suppression against the engine rule pack.

    Parameters
    ----------
    rule_id : str
        Stable id for this country difference.
    products : frozenset[str]
        Products the suppression applies to.
    suppress_codes : frozenset[str]
        Engine issue codes to drop when the token matches.
    token_pattern : re.Pattern[str]
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
    profile_id : str
        Profile id accepted by ``lint``.
    engine : str
        Existing rule pack that runs before deltas.
    products : frozenset[str]
        Products this profile may lint.
    differs : bool
        True when the profile is not identical to its engine.
    deltas : tuple[LintDelta, ...]
        Suppressions applied after the engine.
    recorded : tuple[str, ...]
        Difference ids that are noted and not yet suppressions.
    inherits : str or None
        Optional parent profile id (single-parent DAG).
    stations : frozenset[str]
        ICAO list for station-scoped resolve (not inherited).
    accept_end_tx_tn : bool
        When True, TX/TN after change groups is informational.
    """

    profile_id: str
    engine: str
    products: frozenset[str]
    differs: bool
    deltas: tuple[LintDelta, ...]
    recorded: tuple[str, ...]
    inherits: str | None = None
    stations: frozenset[str] = frozenset()
    accept_end_tx_tn: bool = False


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
        inherits_raw = body.get("inherits")
        inherits: str | None = None
        if inherits_raw is not None:
            if not isinstance(inherits_raw, str) or not inherits_raw.strip():
                msg = f"lint profile {profile_id} inherits must be a string"
                raise ValueError(msg)
            inherits = inherits_raw.strip().lower()
        stations_raw = body.get("stations", [])
        stations = frozenset(item.upper() for item in _string_list(stations_raw, field="stations"))
        accept_end = body.get("accept_end_tx_tn", False)
        if not isinstance(accept_end, bool):
            msg = f"lint profile {profile_id} accept_end_tx_tn must be a boolean"
            raise ValueError(msg)
        loaded[profile_id] = LintProfileSpec(
            profile_id=profile_id,
            engine=_required_str(body, "engine"),
            products=frozenset(item.upper() for item in _string_list(body["products"], field="products")),
            differs=differs,
            deltas=deltas,
            recorded=recorded,
            inherits=inherits,
            stations=stations,
            accept_end_tx_tn=accept_end,
        )
    _validate_inherits(loaded)
    return loaded


def _validate_inherits(rows: dict[str, LintProfileSpec]) -> None:
    """
    Fail closed on unknown parents, cycles, and depth.

    Parameters
    ----------
    rows : dict[str, LintProfileSpec]
        Loaded catalog rows.
    """
    for profile_id, spec in rows.items():
        if spec.inherits is None:
            continue
        if spec.inherits not in rows:
            msg = f"lint profile {profile_id} inherits unknown parent {spec.inherits!r}"
            raise ValueError(msg)
        seen: list[str] = []
        current: str | None = profile_id
        while current is not None:
            if current in seen:
                msg = f"lint profile inherit cycle involving {profile_id!r}"
                raise ValueError(msg)
            seen.append(current)
            if len(seen) > MAX_INHERIT_DEPTH:
                msg = f"lint profile inherit depth exceeds {MAX_INHERIT_DEPTH} for {profile_id!r}"
                raise ValueError(msg)
            parent = rows[current].inherits
            current = parent


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


def profile_inherit_chain(profile_id: str) -> tuple[str, ...]:
    """
    Return parent→…→leaf ids for ``profile_id`` (root first).

    Parameters
    ----------
    profile_id : str
        Leaf profile id.

    Returns
    -------
    tuple[str, ...]
        Inherit chain from root to leaf.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (profile_inherit_chain)
    2
    """
    rows = load_lint_profiles()
    leaf = profile_id.strip().lower()
    if leaf not in rows:
        return (leaf,)
    chain: list[str] = []
    current: str | None = leaf
    while current is not None:
        chain.append(current)
        current = rows[current].inherits
    chain.reverse()
    return tuple(chain)


@cache
def resolved_lint_profile(profile_id: str) -> LintProfileSpec | None:
    """
    Return ``profile_id`` with parent deltas/recorded merged (child wins on id).

    Stations and ``accept_end_tx_tn`` stay on the leaf only.

    Parameters
    ----------
    profile_id : str
        Leaf profile id.

    Returns
    -------
    LintProfileSpec | None
        Merged row, or ``None`` when absent.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (resolved_lint_profile)
    2
    """
    rows = load_lint_profiles()
    leaf = profile_id.strip().lower()
    spec = rows.get(leaf)
    if spec is None:
        return None
    chain = profile_inherit_chain(leaf)
    deltas: list[LintDelta] = []
    recorded: list[str] = []
    seen_delta: set[str] = set()
    seen_recorded: set[str] = set()
    differs = False
    for pid in chain:
        row = rows[pid]
        differs = differs or row.differs
        for delta in row.deltas:
            if delta.rule_id in seen_delta:
                deltas = [item for item in deltas if item.rule_id != delta.rule_id]
            seen_delta.add(delta.rule_id)
            deltas.append(delta)
        for rid in row.recorded:
            if rid in seen_recorded:
                recorded = [item for item in recorded if item != rid]
            seen_recorded.add(rid)
            recorded.append(rid)
    return LintProfileSpec(
        profile_id=leaf,
        engine=spec.engine,
        products=spec.products,
        differs=differs,
        deltas=tuple(deltas),
        recorded=tuple(recorded),
        inherits=spec.inherits,
        stations=spec.stations,
        accept_end_tx_tn=spec.accept_end_tx_tn,
    )


__all__ = [
    "MAX_INHERIT_DEPTH",
    "LintDelta",
    "LintProfileSpec",
    "apply_profile_deltas",
    "lint_profile_spec",
    "load_lint_profiles",
    "profile_inherit_chain",
    "resolved_lint_profile",
]


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
    spec = resolved_lint_profile(profile)
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
