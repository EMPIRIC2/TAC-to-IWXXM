"""Optional store ports — callers inject writers; package stays DB-free."""

from __future__ import annotations

from typing import Protocol

from workflows.models import WorkflowResult


class StorePort(Protocol):
    """
    Callable port for ``onValid.store`` / ``onInvalid.store``.

    Parameters
    ----------
    result :
        Completed workflow result.
    sink :
        Sink id from the workflow YAML (e.g. ``iwxxm_reports``).
    """

    def __call__(self, result: WorkflowResult, *, sink: str) -> None:
        """Persist or quarantine the result for ``sink``."""


__all__ = ["StorePort"]
