"""Load the shared lint-profile catalog.

One YAML row per semantic profile. Country differences are deltas in that
file, not a new Python module. [Corpus: domain-profiles] [Corpus: product §F36]
"""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from functools import cache

from tac_validate.lint_profile_catalog.load import *
from tac_validate.lint_profile_catalog.models import *
from tac_validate.lint_profile_ids import canonical_lint_profile_id
from tac_validate.models import Issue, LintReport


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

    """
    rows = load_lint_profiles()
    leaf = canonical_lint_profile_id(profile_id)
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
        station_prefixes=spec.station_prefixes,
        accept_end_tx_tn=spec.accept_end_tx_tn,
    )


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


__all__ = [
    "MAX_INHERIT_DEPTH",
    "_suppressed",
    "apply_profile_deltas",
    "resolved_lint_profile",
]
