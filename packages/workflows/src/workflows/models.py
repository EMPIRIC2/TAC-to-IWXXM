"""Workflow models — ADR-042."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class WorkflowMessage:
    """
    Input message for ``execute``.

    Parameters
    ----------
    tac : str
        TAC text (or bulletin fragment).
    product : str
        Product id (e.g. ``METAR``).
    job_id : str, optional
        Caller correlation id (F8 ingest job id). By default ``''``.
    meta : dict[str, object], optional
        Optional opaque caller metadata. By default an empty dict.
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
    id : str
        Stable workflow id.
    version : str
        Semver pin for DSL changes.
    pipeline : list[str]
        Ordered stage ids.
    profile_id : str, optional
        Conversion profile id (may be env-resolved). By default ``'annex3'``.
    iwxxm_version : str, optional
        IWXXM version string. By default ``'2025-2'``.
    description : str, optional
        Optional human description. By default ``''``.
    on_valid_store : list[str], optional
        Sink refs from ``onValid.store``. By default an empty list.
    on_invalid_store : list[str], optional
        Sink refs from ``onInvalid.store``. By default an empty list.
    raw : dict[str, object], optional
        Original mapping after env resolve (debug). By default an empty dict.
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
    """
    Structured diagnostic from one stage.

    Attributes
    ----------
    stage : str
        Stage.
    severity : str
        Severity.
    code : str
        Code.
    message : str
        Message text.
    """

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
    ok : bool
        True when all stages passed (soft-pass rules applied).
    workflow_id : str
        Resolved workflow id.
    product : str
        Product used.
    profile : str
        Profile used.
    xml : str or None, optional
        IWXXM XML when convert succeeded. By default ``None``.
    issues : list[StageIssue], optional
        Aggregated diagnostics. By default an empty list.
    stage_failed : str or None, optional
        First failing stage id, if any. By default ``None``.
    job_id : str, optional
        Echo of message job_id. By default ``''``.
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
