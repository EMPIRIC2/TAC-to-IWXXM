"""Part 3 of ``validation_orchestrator.py`` (line-cap split)."""

from .validation_orchestrator_part_2 import ValidationOrchestrator, _orchestrator_instance


def get_validation_orchestrator() -> ValidationOrchestrator:
    """
    Get singleton validation orchestrator instance.


    Returns
    -------
    object
        Return value.
    """
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = ValidationOrchestrator()
    return _orchestrator_instance
