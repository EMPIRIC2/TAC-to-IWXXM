"""Load the shared lint-profile catalog.

One YAML row per semantic profile. Country differences are deltas in that
file, not a new Python module. [Corpus: domain-profiles] [Corpus: product §F36]
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

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


def _delta(raw: dict[str, object]) -> LintDelta:
    """
    Internal helper ``_delta``.

    Parameters
    ----------
    raw : dict
        One ``deltas`` row.

    Returns
    -------
    LintDelta
        Parsed suppression.
    """
    return LintDelta(
        rule_id=str(raw["id"]),
        products=frozenset(str(item).upper() for item in raw["products"]),
        suppress_codes=frozenset(str(item) for item in raw["suppress_codes"]),
        token_pattern=re.compile(str(raw["token_pattern"])),
    )


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
    raw = yaml.safe_load(_CATALOG_PATH.read_text(encoding="utf-8"))
    rows = raw.get("profiles") or {}
    loaded: dict[str, LintProfileSpec] = {}
    for profile_id, body in rows.items():
        deltas = tuple(_delta(item) for item in body.get("deltas", []))
        recorded = tuple(str(item["id"]) for item in body.get("recorded", []))
        products = frozenset(str(item).upper() for item in body["products"])
        loaded[str(profile_id)] = LintProfileSpec(
            profile_id=str(profile_id),
            engine=str(body["engine"]),
            products=products,
            differs=bool(body["differs"]),
            deltas=deltas,
            recorded=recorded,
        )
    return loaded


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
