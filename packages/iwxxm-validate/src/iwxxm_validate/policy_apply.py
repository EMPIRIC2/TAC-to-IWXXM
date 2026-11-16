"""Apply resolved IWXXM output policies to validation reports."""

from __future__ import annotations

from iwxxm_validate.inventory import load_assert_inventory
from iwxxm_validate.models import Issue, StageResult, ValidationReport
from iwxxm_validate.models.policy import PolicyError


def apply_output_policy_to_report(
    report: ValidationReport,
    policy_id: str,
    *,
    profile: str | None = None,
) -> ValidationReport:
    """
    Drop disabled Schematron assert ids. Other issue codes stay on the report.


    Parameters
    ----------
    report : ValidationReport
        Report.
    policy_id : str
        Policy ID.
    profile : str or None, optional
        Profile id. By default ``None``.

    Returns
    -------
    ValidationReport
        Drop disabled Schematron assert ids. Other issue codes stay on the report.
    """
    from iwxxm_validate.policy import load_output_policy_catalog, resolve_output_policy

    catalog = load_output_policy_catalog(profile)
    doc = catalog.get(policy_id)
    if doc is None:
        msg = f"unknown IWXXM output policy {policy_id!r}"
        raise PolicyError(msg)
    resolved = resolve_output_policy(doc, policies=catalog)
    known = load_assert_inventory(doc.pin)

    def keep(issue: Issue) -> bool:
        """
        Return whether ``issue`` stays on the report.

        Schematron issues whose code is in the pin inventory are kept only
        when that code is enabled. Other layers and unknown codes stay.

        Parameters
        ----------
        issue : Issue
            Finding from the validation report.

        Returns
        -------
        bool
            True when the issue is kept.
        """
        if issue.layer != "schematron":
            return True
        if issue.code not in known:
            return True
        return issue.code in resolved.enabled

    issues = [issue for issue in report.issues if keep(issue)]
    stages: list[StageResult] = []
    for stage in report.stages:
        kept = [issue for issue in stage.issues if keep(issue)]
        stages.append(
            StageResult(
                stage=stage.stage,
                label=stage.label,
                ok=not any(issue.severity == "error" for issue in kept),
                issues=kept,
            )
        )
    ok = not any(issue.severity == "error" for issue in issues)
    return ValidationReport(
        ok=ok,
        iwxxm_version=report.iwxxm_version,
        profile=report.profile,
        issues=issues,
        stages=stages,
    )


__all__ = ["apply_output_policy_to_report"]
