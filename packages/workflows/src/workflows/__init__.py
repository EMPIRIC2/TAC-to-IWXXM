"""MET workflow YAML executor — ``execute(message, workflow)`` (ADR-042)."""

from __future__ import annotations

from workflows.execute import WorkflowExecuteError, execute
from workflows.loader import WorkflowLoadError, default_workflows_dir, load_workflow
from workflows.models import (
    StageIssue,
    WorkflowDefinition,
    WorkflowMessage,
    WorkflowResult,
)

__version__ = "0.1.0"

__all__ = [
    "StageIssue",
    "WorkflowDefinition",
    "WorkflowExecuteError",
    "WorkflowLoadError",
    "WorkflowMessage",
    "WorkflowResult",
    "__version__",
    "default_workflows_dir",
    "execute",
    "load_workflow",
]
