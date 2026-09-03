"""Workflow models — ADR-042."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class WorkflowMessage:
    """
    Input message for ``execute``.

    Parameters
    ----------
    tac :
        TAC text (or bulletin fragment).
    product :
        Product id (e.g. ``METAR``).
    job_id :
        Caller correlation id (F8 ingest job id).
    meta :
        Optional opaque caller metadata.
    """

    tac: str
    product: str
    job_id: str = ""
    meta: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class WorkflowDefinition:
    """
    Parsed WorkflowDefinition DSL (v1).

    Parameters
    ----------
    id :
        Stable workflow id.
    version :
        Semver pin for DSL changes.
    pipeline :
        Ordered stage ids.
    profile_id :
        Conversion profile id (may be env-resolved).
    iwxxm_version :
        IWXXM version string.
    description :
        Optional human description.
    on_valid_store :
        Sink refs from ``onValid.store``.
    on_invalid_store :
        Sink refs from ``onInvalid.store``.
    raw :
        Original mapping after env resolve (debug).
    """

    id: str
    version: str
    pipeline: list[str]
    profile_id: str = "annex3"
    iwxxm_version: str = "2025-2"
    description: str = ""
    on_valid_store: list[str] = field(default_factory=list)
    on_invalid_store: list[str] = field(default_factory=list)
    raw: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class StageIssue:
    """Structured diagnostic from one stage."""

    stage: str
    severity: str
    code: str
    message: str


@dataclass(slots=True)
class WorkflowResult:
    """
    Outcome of ``execute``.

    Parameters
    ----------
    ok :
        True when all stages passed (soft-pass rules applied).
    workflow_id :
        Resolved workflow id.
    product :
        Product used.
    profile :
        Profile used.
    xml :
        IWXXM XML when convert succeeded.
    issues :
        Aggregated diagnostics.
    stage_failed :
        First failing stage id, if any.
    job_id :
        Echo of message job_id.
    """

    ok: bool
    workflow_id: str
    product: str
    profile: str
    xml: str | None = None
    issues: list[StageIssue] = field(default_factory=list)
    stage_failed: str | None = None
    job_id: str = ""


__all__ = [
    "StageIssue",
    "WorkflowDefinition",
    "WorkflowMessage",
    "WorkflowResult",
]
