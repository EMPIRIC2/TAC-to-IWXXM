"""Ingest pipeline: workflows.execute (F8 / ADR-018 / ADR-042)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from metar_worker.poller import IngestJob
from workflows import WorkflowMessage, execute

# Map ADR-042 stage ids → legacy PipelineResult.stage_failed / issue stage names.
_LEGACY_STAGE = {
    "validate-tac": "lint",
    "convert-iwxxm": "convert",
    "validate-xsd": "iwxxm_validate",
    "validate-schematron": "iwxxm_validate",
}


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
        First failing stage name, if any (legacy ids: lint / convert / iwxxm_validate).
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
    workflow_id: str = "f8-metar-ingest-default",
) -> PipelineResult:
    """
    Run ``execute(message, workflow)`` for one job (ADR-042).

    Failures quarantine (caller writes quarantine row); success is store-ready.
    ``profile`` / ``iwxxm_version`` override YAML when provided (worker Settings).
    """
    from workflows.loader import load_workflow
    from workflows.models import WorkflowDefinition

    product = job.product.upper()
    profile_l = profile.lower()
    skip = frozenset({"validate-tac"}) if skip_lint else frozenset()

    definition: WorkflowDefinition = load_workflow(workflow_id)
    # Worker env overrides beat unresolved empty ${ENV:} defaults.
    definition = WorkflowDefinition(
        id=definition.id,
        version=definition.version,
        pipeline=list(definition.pipeline),
        profile_id=profile_l,
        iwxxm_version=iwxxm_version,
        description=definition.description,
        on_valid_store=list(definition.on_valid_store),
        on_invalid_store=list(definition.on_invalid_store),
        raw=definition.raw,
    )

    wf = execute(
        WorkflowMessage(tac=job.tac, product=product, job_id=job.job_id),
        definition,
        skip_stages=skip,
    )

    issues = [
        {
            "stage": _LEGACY_STAGE.get(issue.stage, issue.stage),
            "severity": issue.severity,
            "code": issue.code,
            "message": issue.message,
        }
        for issue in wf.issues
    ]
    stage_failed = None
    if wf.stage_failed is not None:
        stage_failed = _LEGACY_STAGE.get(wf.stage_failed, wf.stage_failed)

    return PipelineResult(
        job_id=job.job_id,
        ok=wf.ok,
        product=product,
        profile=profile_l,
        xml=wf.xml,
        issues=issues,
        stage_failed=stage_failed,
    )


__all__ = ["PipelineResult", "process_job"]
