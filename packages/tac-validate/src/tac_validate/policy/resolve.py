"""TAC quality policy load + resolve.

Draft lifecycle warns on unknown registry codes; activate fails closed.
"""

# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from tac_validate.issue_registry import ISSUES, by_code, catalog_entries
from tac_validate.models import Issue, LintReport
from tac_validate.policy.load import *
from tac_validate.policy.models import *


def resolve_policy(
    doc: PolicyDocument,
    *,
    policies: Mapping[str, PolicyDocument],
    activate: bool = False,
) -> ResolvedPolicy:
    """
    Merge ``extends`` and compute enabled codes.

    Parameters
    ----------
    doc : PolicyDocument
        Leaf policy document.
    policies : Mapping[str, PolicyDocument]
        Catalog keyed by policy id (must include ``doc`` and parents).
    activate : bool, optional
        When True, treat as activation even if ``lifecycle`` is draft (fail closed). By default ``False``.

    Returns
    -------
    ResolvedPolicy
        Merged view with warnings / activation status.

    """
    chain = _chain_docs(doc, policies)
    select: list[str] = []
    ignore: set[str] = set()
    severity: dict[str, str] = {}
    preview: set[str] = set()
    detectors: list[str] = []
    product = doc.product
    for item in chain:
        if item.product is not None:
            product = item.product
        if item.select:
            select = list(item.select)
        ignore |= set(item.ignore)
        severity.update(dict(item.severity))
        preview |= set(item.preview)
        if item.detectors:
            detectors = list(item.detectors)

    referenced = set(select) | ignore | set(severity) | preview
    warnings = list(
        _validate_code_refs(
            referenced,
            lifecycle=doc.lifecycle,
            activate=activate,
        )
    )

    defaults = _default_codes_for_product(product)
    enabled = set(select) if select else set(defaults) - preview
    enabled -= ignore
    enabled = {code for code in enabled if not _unknown(code)}

    can_activate = not any("unknown registry code" in w for w in warnings)

    return ResolvedPolicy(
        id=doc.id,
        lifecycle=doc.lifecycle,
        product=product,
        enabled_codes=frozenset(enabled),
        severity_overrides=dict(severity),
        preview_codes=frozenset(preview),
        detector_ids=tuple(detectors),
        warnings=tuple(warnings),
        can_activate=can_activate,
        chain=tuple(item.id for item in chain),
    )


def apply_policy_to_report(
    report: LintReport,
    policy_id: str,
    *,
    profile: str | None = None,
) -> LintReport:
    """
    Keep issues selected by ``policy_id`` and apply severity overrides.

    Parameters
    ----------
    report : LintReport
        Lint report before policy filtering.
    policy_id : str
        TAC quality policy document id.
    profile : str or None, optional
        Profile id. By default ``None``.


    Returns
    -------
    LintReport
        Keep issues selected by ``policy_id`` and apply severity overrides.
    """
    catalog = load_policy_catalog(profile)
    doc = catalog.get(policy_id)
    if doc is None:
        msg = f"unknown TAC quality policy {policy_id!r}"
        raise PolicyError(msg)
    resolved = resolve_policy(doc, policies=catalog, activate=(doc.lifecycle == "activated"))
    selectable = _default_codes_for_product(resolved.product) | resolved.preview_codes
    kept: list[Issue] = []
    for issue in report.issues:
        # Parse-gate / AHL codes outside the product catalog always pass.
        if issue.code not in resolved.enabled_codes and issue.code in selectable:
            continue
        severity = resolved.severity_overrides.get(issue.code, issue.severity)
        if severity == issue.severity:
            kept.append(issue)
            continue
        kept.append(
            Issue(
                severity=severity,
                code=issue.code,
                message=issue.message,
                location=issue.location,
                start=issue.start,
                end=issue.end,
            )
        )
    ok = not any(item.severity == "error" for item in kept)
    return LintReport(
        ok=ok,
        product=report.product,
        issues=kept,
        fixes=list(report.fixes),
        profile=report.profile,
    )


__all__ = [
    "ENV_POLICY_DIR",
    "ISSUES",
    "MAX_EXTENDS_DEPTH",
    "_SEVERITIES",
    "Any",
    "Issue",
    "LintReport",
    "Literal",
    "Mapping",
    "PolicyLifecycle",
    "apply_policy_to_report",
    "by_code",
    "catalog_entries",
    "resolve_policy",
]
