"""``execute(message, workflow)`` — ADR-042."""

from __future__ import annotations

from pathlib import Path

from workflows.loader import WorkflowLoadError, load_workflow
from workflows.models import StageIssue, WorkflowDefinition, WorkflowMessage, WorkflowResult
from workflows.ports import StorePort
from workflows.stages import STAGE_REGISTRY, run_stage


class WorkflowExecuteError(ValueError):
    """Raised for fail-closed execute errors (unknown stage, bad workflow)."""


def execute(
    message: WorkflowMessage,
    workflow: str | WorkflowDefinition,
    *,
    workflows_dir: Path | None = None,
    store_valid: StorePort | None = None,
    store_invalid: StorePort | None = None,
    skip_stages: frozenset[str] | None = None,
) -> WorkflowResult:
    """
    Run a workflow pipeline against ``message``.

    Parameters
    ----------
    message :
        TAC + product (+ optional job_id).
    workflow :
        Workflow id string or already-parsed definition.
    workflows_dir :
        Override YAML search path.
    store_valid :
        Optional ``onValid.store`` callback.
    store_invalid :
        Optional ``onInvalid.store`` callback.
    skip_stages :
        Stage ids to omit (F8 ``skip_lint`` maps to ``validate-tac``).

    Returns
    -------
    WorkflowResult
        Aggregate outcome; first failing stage halts the pipeline.
    """
    if isinstance(workflow, str):
        try:
            definition = load_workflow(workflow, workflows_dir=workflows_dir)
        except WorkflowLoadError as exc:
            raise WorkflowExecuteError(str(exc)) from exc
    else:
        definition = workflow

    skip = skip_stages or frozenset()
    pipeline = [s for s in definition.pipeline if s not in skip]
    issues: list[StageIssue] = []
    xml: str | None = None
    product = message.product.upper()

    for stage_id in pipeline:
        if stage_id not in STAGE_REGISTRY:
            msg = f"unknown stage id: {stage_id}"
            raise WorkflowExecuteError(msg)
        outcome = run_stage(stage_id, message, definition, xml=xml)
        issues.extend(outcome.issues)
        if outcome.xml is not None:
            xml = outcome.xml
        if not outcome.ok:
            result = WorkflowResult(
                ok=False,
                workflow_id=definition.id,
                product=product,
                profile=definition.profile_id,
                xml=xml,
                issues=issues,
                stage_failed=stage_id,
                job_id=message.job_id,
            )
            _dispatch_stores(result, definition, store_valid=None, store_invalid=store_invalid)
            return result

    result = WorkflowResult(
        ok=True,
        workflow_id=definition.id,
        product=product,
        profile=definition.profile_id,
        xml=xml,
        issues=issues,
        stage_failed=None,
        job_id=message.job_id,
    )
    _dispatch_stores(result, definition, store_valid=store_valid, store_invalid=None)
    return result


def _dispatch_stores(
    result: WorkflowResult,
    definition: WorkflowDefinition,
    *,
    store_valid: StorePort | None,
    store_invalid: StorePort | None,
) -> None:
    if result.ok and store_valid is not None:
        for sink in definition.on_valid_store:
            store_valid(result, sink=sink)
    if not result.ok and store_invalid is not None:
        for sink in definition.on_invalid_store:
            store_invalid(result, sink=sink)


__all__ = ["WorkflowExecuteError", "execute"]
