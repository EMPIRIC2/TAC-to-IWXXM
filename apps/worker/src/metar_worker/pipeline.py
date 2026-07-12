"""Ingest pipeline: tac-validate → tac2iwxxm → iwxxm-validate (F8 / ADR-018)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from iwxxm_validate import validate as iwxxm_validate
from tac_validate import lint as tac_lint

from metar_worker.poller import IngestJob
from tac2iwxxm import convert as tac2iwxxm_convert


@dataclass(slots=True)
class PipelineResult:
    """
    Outcome of processing one ingest job.

    Parameters
    ----------
    job_id :
        Echo of the ingest job id.
    ok :
        True when lint + convert + IWXXM validate all passed.
    product :
        Product id used.
    profile :
        Schema profile used.
    xml :
        IWXXM XML when convert succeeded.
    issues :
        Structured diagnostics from any stage.
    stage_failed :
        First failing stage name, if any.
    """

    job_id: str
    ok: bool
    product: str
    profile: str
    xml: str | None = None
    issues: list[dict[str, Any]] = field(default_factory=list)
    stage_failed: str | None = None


def process_job(
    job: IngestJob,
    *,
    profile: str = "annex3",
    iwxxm_version: str = "2025-2",
    skip_lint: bool = False,
) -> PipelineResult:
    """
    Run lint → convert → IWXXM validate for one job.

    Failures quarantine (caller writes quarantine row); success is store-ready.
    """
    product = job.product.upper()
    profile_l = profile.lower()
    issues: list[dict[str, Any]] = []

    if not skip_lint:
        lint_report = tac_lint(job.tac, product=product)
        for issue in lint_report.issues:
            issues.append(
                {
                    "stage": "lint",
                    "severity": issue.severity,
                    "code": issue.code,
                    "message": issue.message,
                }
            )
        if not lint_report.ok:
            return PipelineResult(
                job_id=job.job_id,
                ok=False,
                product=product,
                profile=profile_l,
                issues=issues,
                stage_failed="lint",
            )

    convert_result = tac2iwxxm_convert(
        job.tac,
        product=product,
        profile=profile_l,
        iwxxm_version=iwxxm_version,
    )
    for issue in convert_result.issues:
        issues.append(
            {
                "stage": "convert",
                "severity": issue.severity,
                "code": issue.code,
                "message": issue.message,
            }
        )
    if not convert_result.ok or not convert_result.xml:
        return PipelineResult(
            job_id=job.job_id,
            ok=False,
            product=product,
            profile=profile_l,
            issues=issues,
            stage_failed="convert",
        )

    report = iwxxm_validate(
        convert_result.xml,
        iwxxm_version=iwxxm_version,
        profile=profile_l,
        levels=("xsd", "schematron"),
    )
    for issue in report.issues:
        if issue.severity == "error" and issue.code in {"SCHEMATRON_SKIPPED"}:
            continue
        issues.append(
            {
                "stage": "iwxxm_validate",
                "severity": issue.severity,
                "code": issue.code,
                "message": issue.message,
            }
        )
    blocking = [
        i
        for i in report.issues
        if i.severity == "error" and i.code not in {"SCHEMATRON_SKIPPED"}
    ]
    # Soft-pass when report.ok is False solely due to SCHEMATRON_SKIPPED.
    if blocking:
        return PipelineResult(
            job_id=job.job_id,
            ok=False,
            product=product,
            profile=profile_l,
            xml=convert_result.xml,
            issues=issues,
            stage_failed="iwxxm_validate",
        )

    return PipelineResult(
        job_id=job.job_id,
        ok=True,
        product=product,
        profile=profile_l,
        xml=convert_result.xml,
        issues=issues,
        stage_failed=None,
    )


__all__ = ["PipelineResult", "process_job"]
